const { DataTypes } = require('sequelize');

module.exports.SessionsModel = (sequelize) => {
    return sequelize.define(
        'Sessions',
        {
            id: {
                type: DataTypes.INTEGER,
                primaryKey: true,
                autoIncrement: true,
                allowNull: false,
            },
            host_id: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            user_id: {
                type: DataTypes.TEXT,
                allowNull: false,
            },
            duration: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            date_begin: {
                type: DataTypes.DATE,
                allowNull: false,
            },
            date_end: {
                type: DataTypes.DATE,
                allowNull: true,
            },
        },
        {
            tableName: 'sessions',
            timestamps: false
        }
    );
};
