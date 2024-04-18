/* abstract */ class SessionStore {
    findSession(id) {}
    createSession(id) {}
    deleteSession(id, session) {}
    getAllSessions() {}
    appendTimerToSession(id, timer) {}
}

class InMemorySessionStore extends SessionStore {
    constructor() {
        super();
        this.sessions = new Map();
    }

    findSession(id) {
        return this.sessions.get(id);
    }

    createSession(id, session) {
        this.sessions.set(id, session);
    }

    deleteSession(id) {
        this.sessions.delete(id);
    }

    getAllSessions() {
        return Array.from(this.sessions.values());
    }

    appendTimerToSession(id, timer) {
        const session = this.sessions.get(id);
        session.timer = timer;
        this.sessions.set(id, session);
    }
}

module.exports = {
    InMemorySessionStore
};