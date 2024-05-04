const { ProductsModel, UserBalanceModel, UserProductsModel, sequelize } = require('../db');
const { Op } = require('sequelize');

module.exports.getActiveTarificationScheme = async () => {
    // get the active tarification scheme from the database via raw query
    // get id of billing_prifilee from value column of config table where name is 'billing_profile_id'
    // get tarification scheme from billing_profile table where id is the id from previous query
    billingProfileId = await sequelize.query(
        'SELECT value FROM config WHERE name = "billing_profile_id"',
        { type: sequelize.QueryTypes.SELECT }
    );
    billingProfileId = billingProfileId[0].value;

    tarificationScheme = await sequelize.query(
        `SELECT sheme FROM billing_profiles WHERE id = ${billingProfileId}`,
        { type: sequelize.QueryTypes.SELECT }
    );
    return tarificationScheme[0].sheme;
}

module.exports.withdrawTime = async (user_id, price_per_sec, seconds) => {
    // first, check if user has any active products with descnding ordeer of priority_level
    // then, get the product with the highest priority_level
    let switch_to_balance = false;

    const balance = await UserBalanceModel.findOne({
        where: {
            user_id: user_id,
            currency_id: 1
        }
    });
    // find the active product with the highest priority level. use join beacuse priority level is in products table
    const product = await UserProductsModel.findOne({
        where: {
            user_id: user_id,
            status: 'active'
        },
        include: [
            {
                model: ProductsModel,
                required: true
            }
        ],
        order: [
            [ProductsModel, 'priority_level', 'DESC']
        ]
    });
    // if user has active product, then add played_time seconds to the product
    // then, check if the product has enough time to play or not expired by getting datat from product table
    if (product !== null) {
        const played_time = parseInt(product.played_time) + parseInt(seconds);
        const product_info = await ProductsModel.findOne({
            where: {
                id: product.product_id
            }
        });
        // check if we didn't exceed the lifetime by calculating diff between current time and purchase_date
        //get current time according to the TZ of the server
        let current_time = new Date();
        // add 3 hours to the current time
        current_time.setHours(current_time.getHours() + 3);
        console.log("🕒 Current time:", current_time);
        const purchase_date = product.purchase_date;
        const diff = current_time - purchase_date;
        const diff_in_seconds = diff / 1000;
        console.log("🕒 Diff in seconds:", diff_in_seconds);
        console.log("🕒 Product lifetime:", product_info.lifetime);
        if (diff_in_seconds <= product_info.lifetime) {
            // check if we did't exceed the time limit
            console.log("🛒 Product has time to live");
            if (played_time <= product_info.included_time) {
                // add played time
                product.played_time = played_time;
                await product.save();
                console.log("🛒 Product updated");
                return {
                    balance: balance.balance,
                    mode: 'product',
                    product_id: product.product_id,
                    remaining_time: product_info.included_time - played_time,
                    action: 'product_update'
                }
            }
            else {
                // add played time and make status 'expired'
                product.status = 'expired';
                await product.save();
                console.log("🛒 play time exceeded");
                switch_to_balance = true;
            }
        } else {
            // make status 'expired' if we exceed the lifetime
            console.log("🛒 Product expired: ", product.status);
            product.status = 'expired';
            await product.save();
            // ensure to withdraw from balance
            switch_to_balance = true;
        }
    } else {
        // ensure to withdraw from balance
        console.log("🛒 No active product");
        switch_to_balance = true;
    }
    // if we have to withdraw from balance, then do it
    if (switch_to_balance) {
        const new_balance = balance.balance - price_per_sec * seconds;
        await UserBalanceModel.update({
            balance: new_balance
        }, {
            where: {
                user_id: user_id,
                currency_id: 1
            }
        });
        if (new_balance < 0) {
            return {
                balance: balance.balance,
                mode: 'balance',
                action: 'disconnect'
            }
        } else {
            return {
                balance: new_balance,
                mode: 'balance',
                action: 'balance_update'
            }
        }
    }
}
