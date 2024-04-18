const { DataTypes } = require('sequelize');

module.exports.UserProductsModel = (sequelize) => {
    return sequelize.define(
        'UserProducts',
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
            product_id: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            played_time: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            status: {
                type: DataTypes.TEXT,
                allowNull: false,
            },
            purchase_date: {
                type: DataTypes.DATE,
                allowNull: false,
            },
            activation_date: {
                type: DataTypes.DATE,
                allowNull: true,
            },
        },
        {
            tableName: 'user_products',
            timestamps: false
        }
    );
}