const { DataTypes } = require('sequelize');

module.exports.HostsModel = (sequelize) => {
    return sequelize.define(
        'Hosts',
        {
            id: {
				type: DataTypes.INTEGER,
				primaryKey: true,
				autoIncrement: true,
				allowNull: false,
			},
            name: {
                type: DataTypes.TEXT,
                allowNull: false,
            },
            identifier: {
                type: DataTypes.TEXT,
                allowNull: false,
            },
            player_id: {
                type: DataTypes.TEXT,
                allowNull: false,
            },
            status: {
                type: DataTypes.TEXT,
                allowNull: false,
            },
            is_enabled: {
                type: DataTypes.TINYINT,
                allowNull: false,
            }
        },
        {
            tableName: 'hosts',
            timestamps: false
        }
    );
};
