const { DataTypes } = require('sequelize');

module.exports.ProductsModel = (sequelize) => {
    return sequelize.define(
        'Products',
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
            priority_level: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            included_time: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            lifetime: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            available_options: {
                type: DataTypes.JSON,
                allowNull: false,
            },
            coast_sheme: {
                type: DataTypes.JSON,
                allowNull: false,
            },
        },
        {
            tableName: 'products',
            timestamps: false
        }
    );
}