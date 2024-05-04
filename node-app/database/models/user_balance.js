const { DataTypes } = require('sequelize');

module.exports.UserBalanceModel = (sequelize) => {
    return sequelize.define(
        'UserBalance',
        {
            id: {
                type: DataTypes.INTEGER,
                primaryKey: true,
                autoIncrement: true,
                allowNull: false,
            },
            user_id: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            currency_id: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            balance: {
                type: DataTypes.FLOAT,
                allowNull: false,
            },
        },
        {
            tableName: 'user_balance',
            timestamps: false
        }
    );
}