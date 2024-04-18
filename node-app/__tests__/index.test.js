// perform test on our server
const io = require('socket.io-client');

let socket;
const identifier = '00:25:96:FF:FE:12:34:56';
const base_id = '00:25:96:FF:FE:12:34:56';
const valid_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im9uaXh4IiwiZXhwIjoxNzE0MDY0NDgxfQ.INl6wiKKq5aX0pB-Y1Dv4sCtc59Z9fhltMcSZpboWy0'
beforeAll((done) => {
    // Setup
    socket = io(`http://localhost:8866`, {
      'reconnection delay': 0,
      'reopen delay': 0,
      'force new connection': true,
      transports: ['websocket'],
      query: {
        identifier: identifier
      }
    });
    socket.on('connect', () => {
      done();
    });
  });

afterEach((done) => {
    // Cleanup
    if (socket.connected) {
      socket.disconnect();
    }
    socket = io(`http://localhost:8866`, {
      'reconnection delay': 0,
      'reopen delay': 0,
      transports: ['websocket'],
      query: {
        identifier: identifier
      }
    });
    done();
  });

afterAll((done) => {
    // Cleanup
    if (socket.connected) {
      socket.disconnect();
    }
    done();
  });

describe('test socket.io server methods', () => {
    test('should retun not_found if incorrect identifier or online if ok', (done) => {
        socket.on('host_online', (data) => {
            const check = identifier === base_id ? 'online' : 'not_found';
            expect(data.status).toBe(check);
            done();
        });
    });

    test('should return invalid_token if token is invalid', (done) => {
        socket.emit('start_session', 'invalid_token');
        // expect call of invalid_token event without any data
        socket.on('invalid_token', () => {
            done();
        });
        // if start_session recieved -> fail
        socket.on('start_session', () => {
            done.fail();
        });
    });

    test('should return session_id and player_id if token is valid', (done) => {
        socket.on('host_online', (data) => {
            expect(data.status).toBe('online');
            socket.emit('start_session', valid_token);
            socket.on('session_started', (data) => {
                expect(data.session_id).toBeDefined();
                expect(data.player_id).toBeDefined();
                // wait until tarification event is emitted
                socket.on('server_message', (data) => {
                    expect(data).toBeDefined();
                    // close session with empty data
                    socket.emit('end_session', {});
                    done();
                });
            });
        });
    });

    test('test continious server_messages', (done) => {
        socket.on('host_online', (data) => {
            socket.emit('start_session', valid_token);
            socket.on('session_started', () => {
                let counter = 0;
                socket.on('server_message', (data) => {
                    counter++;
                    if (counter === 5) {
                        socket.emit('end_session', {});
                        done();
                    }
                });
            });
        });
    }, 11000);
});
