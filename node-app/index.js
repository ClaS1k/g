const { checkHost, hostOnline, hostOffline, startSession, endSession, getAllHosts } = require("./database/controllers/connectionController");
const { getActiveTarificationScheme, withdrawTime } = require("./database/controllers/tarificationController");
const { isTimeBetween } = require("./utils");
const { InMemorySessionStore } = require("./sessionStore");

const { v4: uuidv4 } = require("uuid");
const jwt = require('jsonwebtoken');
const sessionStore = new InMemorySessionStore();
const httpServer = require("http").createServer();
const io = require("socket.io")(httpServer, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"],
        allowedHeaders: ["Authorization"],
        credentials: true
    }
});

// read the .env file
require("dotenv").config();

// print the environment all variables
console.log("🔧 Environment variables:",
    process.env.PORT,
    process.env.SECRET_KEY,
    process.env.TARIFICATION_INTERVAL_SEC
);
// configure constants from the .env file
const port = process.env.SOCKET_PORT || 8766;
const secret = process.env.SECRET_KEY
const tarification_interval_sec = process.env.TARIFICATION_INTERVAL_SEC || 1;

async function calculatePricePerSecond() {
    // get the active tarification scheme
    let tarificationScheme = await getActiveTarificationScheme();
    //calculate price per second from tarification scheme according to the current time
    // get current time and current week day
    const current_week_day = new Date().getDay();
    let price_per_sec = tarificationScheme.default.find((profile) => profile.currency_id === 1).price / 60 / 60;
    console.log('💰 Default price per second:', price_per_sec);
    tarificationScheme.exсeptions.forEach((exception) => {
        if (exception.day_of_week === current_week_day) {
            // check if the current time is between the start and end time of the exception
            if (isTimeBetween(exception.time_from, exception.time_to)) {
                // set the price per second to the price from profile list where currency is 1
                price_per_sec = exception.profile.find((profile) => profile.currency_id === 1).price / 60 / 60;
            }
        }
    });
    console.log('💰 Final price per second:', price_per_sec);
    return price_per_sec;
}
calculatePricePerSecond().then((price_per_sec) => {
    // log the price per second
    console.log("💰 Price per second after call:", price_per_sec);
});

async function doTarification(user_id) {
    // get the current price per second
    const price_per_sec = await calculatePricePerSecond();
    // do tarification
    result = await withdrawTime(user_id, price_per_sec, tarification_interval_sec);
    console.log("💰 Tarification result:", result);
    return result;
}

// handle connection
// clinet should pass idetifier in the query
io.on("connection", (socket) => {
    console.log("🔗 New connection");
    let { identifier } = socket.handshake.query;
    if (!identifier) {
        console.log("❌ No identifier");
        socket.disconnect();
        return;
    }
    console.log("🔑 Identifier:", identifier);
    checkHost(identifier)
        .then((host) => {
            console.log("🔍 Host:", host);
            if (host !== false) {
                // set the host id
                socket.host_id = host;
                console.log("🆔 Host id:", host);
                hostOnline(identifier);
                console.log("🟢 Host online");
                socket.emit("host_online", { status: "online" });
            } else {
                console.log("🔴 Host not found");
                socket.emit("host_online", { status: "not_found" });
                identifier = null;
                socket.disconnect();
            }
        })
        .catch((error) => {
            console.log("❌ Error:", error);
            socket.disconnect();
        });
    socket.on("start_session", (token) => {
        // validate jwt token and get username
        jwt.verify(token, secret, (err, decoded) => {
            if (err) {
                console.log("❌ Invalid token");
                socket.emit("invalid_token");
                return;
            }
            console.log("🔑 Username:", decoded.username);
            console.log("🔑 Host id:", socket.host_id);
            startSession(socket.host_id, decoded.username).then((session) => {
                if (!session) {
                    console.log("❌ Session not started");
                    socket.emit("session_not_started");
                    return;
                }
                console.log("🎮 Session:", session);
                // save session to the store
                sessionStore.createSession(
                    socket.host_id,
                    {
                        id: session.session_id,
                        player_id: session.player_id,
                    }
                );
                // set interval for tarification
                const timer = setInterval(() => {
                    doTarification(session.player_id).then((result) => {
                        if (result.action !== "disconnect") {
                            console.log("💰 Tarification withdraw mode: ", result.mode);
                        } else {
                            console.log("💰 disocnnecting user eveent");
                        }
                        socket.emit("server_message", { message: result });
                    });
                }, tarification_interval_sec * 1000);
                // save timer to the session
                sessionStore.appendTimerToSession(socket.host_id, timer);
                console.log("🎮 Session started");
                socket.emit("session_started", { session_id: session.session_id, player_id: session.player_id});
            });
        });
    });
    socket.on("end_session", () => {
        const session = sessionStore.findSession(socket.host_id);
        if (!session) {
            console.log("❌ No session");
            socket.emit("no_session");
            return;
        }
        // clear the interval
        clearInterval(session.timer);
        // end the session
        endSession(session.id);
        console.log("🎮 Session ended");
        sessionStore.deleteSession(socket.host_id);
        socket.emit("session_ended");
    });
    socket.on("disconnect", () => {
        // check if session is active
        const session = sessionStore.findSession(socket.host_id);
        if (session) {
            // clear the interval
            clearInterval(session.timer);
            // end the session
            endSession(session.id);
            console.log("🎮 Session ended");
            sessionStore.deleteSession(socket.host_id);
        }
        console.log("🔗 Disconnected");
        hostOffline(identifier);
    });
});




httpServer.listen(port, '0.0.0.0', () =>
  console.log(`server listening at http://localhost:${port}`)
);

module.exports = httpServer; // for testing purposes