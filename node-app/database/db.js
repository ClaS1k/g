require('dotenv').config();
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
    process.env.MYSQL_DATABASE,
    process.env.MYSQL_USER,
    process.env.MYSQL_PASSWORD,
    {
        host: process.env.MYSQL_HOST,
        port: process.env.MYSQL_PORT,
        dialect: 'mysql'
    }
);

// test the connection
(async () => {
	try {
		await sequelize.authenticate();
		console.log('💾 Database connection has been established successfully.');
	} catch (error) {
		console.error('Unable to connect to the database:', error);
	}
})();

// init the models
const HostsModel = require('./models/hosts').HostsModel(sequelize);
const SessionsModel = require('./models/sessions').SessionsModel(sequelize);
const UserBalanceModel = require('./models/user_balance').UserBalanceModel(sequelize);
const ProductsModel = require('./models/products').ProductsModel(sequelize);
const UserProductsModel = require('./models/user_products').UserProductsModel(sequelize);

// associations
// user_products belongs to products
UserProductsModel.belongsTo(ProductsModel, { foreignKey: 'product_id' });


module.exports = {
    sequelize,
    HostsModel,
    SessionsModel,
    UserBalanceModel,
    ProductsModel,
    UserProductsModel
};
