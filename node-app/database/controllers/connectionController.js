const { SessionsModel, HostsModel, sequelize } = require('../db');
const { Op } = require('sequelize');

module.exports.checkHost = async (identifier) => {
    // return host id if host exists, else return false
    result = await HostsModel.findOne({
        where: {
            identifier: identifier
        }
    });
    return result !== null ? result.id : false;
}

module.exports.getAllHosts = async () => {
    // return all hosts
    return await HostsModel.findAll();
}

module.exports.hostOnline = async (identifier) => {
    // set status of host to online
    await HostsModel.update({
        status: 'await'
    }, {
        where: {
            identifier: identifier
        }
    });
}

module.exports.hostOffline = async (identifier) => {
    // set status of host to offline
    if (identifier) {
        await HostsModel.update({
            status: 'disabled'
        }, {
            where: {
                identifier: identifier
            }
        });
    }
}

module.exports.startSession = async (host_id, username) => {
    //get user id and  by username via raw query
    let player_id = await sequelize.query(
        `SELECT user_id FROM users WHERE username = '${username}'`,
        { type: sequelize.QueryTypes.SELECT }
    );
    player_id = player_id[0].user_id;
    console.log(player_id);

    // get the current date
    const date_begin = new Date();
    const session = await SessionsModel.create({
        host_id: host_id,
        user_id: player_id,
        duration: 0,
        date_begin: date_begin
    });

    // set status of host to playing
    await HostsModel.update({
        status: 'playing'
    }, {
        where: {
            id: host_id
        }
    });
    // return the session id and player id
    return {
        session_id: session.id,
        player_id: player_id
    };
}

module.exports.endSession = async (session_id) => {
    // get the session
    const session = await SessionsModel.findOne({
        where: {
            id: session_id
        }
    });
    // get the current date
    const date_end = new Date();
    // calculate the duration in seconds
    const duration = (date_end - session.date_begin) / 1000;
    // update the session
    await SessionsModel.update({
        duration: duration,
        date_end: date_end
    }, {
        where: {
            id: session_id
        }
    });
    // set status of host to await
    await HostsModel.update({
        status: 'await'
    }, {
        where: {
            id: session.host_id
        }
    });
}

