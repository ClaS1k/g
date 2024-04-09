import json
import requests
import time
import mysql
import uvicorn
import hashlib
import datetime as dt

import config

from fastapi import FastAPI, Depends, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from typing import Annotated

from mysql import connector

from models import UserCreate, AdminCreate, HostCreate, TransactionCreate, ReservationCreate, BillingProfile, UsergroupCreate, ProductCreate, CurrencyCreate
from validate import *
from sql import *

app = FastAPI()
security = HTTPBasic()

# методы users/*

@app.get("/users")
async def get_all_users(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    users_list = []

    sql = "SELECT * FROM `users`"
    result = sql_query(sql)

    for row in result:
        current_user = {
            "id": row[0],
            "username": row[1],
            "name": row[3],
            "surname": row[4],
            "usergroup_id": row[5],
            "avatar_id": row[6],
            "email": row[7],
            "phone": row[8],
            "country": row[9],
            "city": row[10],
            "address": row[11],
        }

        users_list.append(current_user)
        
    return {"result": users_list}

@app.get("/users/{user_id}")
async def get_user_by_id(user_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
        
    user_data = {
        "username": result[0][1],
        "name": result[0][3],
        "surname": result[0][4],
        "usergroup_id": result[0][5],
        "avatar_id": result[0][6],
        "email": result[0][7],
        "phone": result[0][8],
        "country": result[0][9],
        "city": result[0][10],
        "address": result[0][11],
    }
        
    return {"result": user_data}

@app.get("/users/find/{query}")
async def find_users_by_username(query, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    
    if(len(query) < 2):
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Query must be longer 2 symbols"
        }}

    sql = "SELECT * FROM `users` WHERE LOCATE('"+str(query)+"', `username`)"
    result = sql_query(sql)

    users_list = []

    for row in result:
        current_user = {
            "id": row[0],
            "username": row[1],
            "name": row[3],
            "surname": row[4],
            "usergroup_id": row[5],
            "avatar_id": row[6],
            "email": row[7],
            "phone": row[8],
            "country": row[9],
            "city": row[10],
            "address": row[11],
        }

        users_list.append(current_user)
        
    return {"result": users_list}

@app.get("/users/{username}/username")
async def get_user_by_username(username, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `users` WHERE `username`='" + str(username) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
        
    user_data = {
        "username": result[0][1],
        "name": result[0][3],
        "surname": result[0][4],
        "usergroup_id": result[0][5],
        "avatar_id": result[0][6],
        "email": result[0][7],
        "phone": result[0][8],
        "country": result[0][9],
        "city": result[0][10],
        "address": result[0][11],
    }
        
    return {"result": user_data}

@app.get("/users/{user_id}/balance")
async def get_user_balance(user_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    
    currency_list = []

    sql = "SELECT * FROM `currency`"

    result = sql_query(sql)

    for row in result:
        currency_list.append(row[0])
    
    user_balance_list = []

    for currency in currency_list:
        sql = "SELECT * FROM `user_balance` WHERE `user_id`='" + str(user_id) + "' AND `currency_id`='" + str(currency) + "'"

        result = sql_query(sql)

        if(len(result) == 0):
            sql = "INSERT INTO `user_balance`(`user_id`, `currency_id`, `balance`) VALUES ('" + str(user_id) + "','" + str(currency) + "','0')"

            sql_query(sql)

            current_currency = {
                "currency_id": currency,
                "balance": 0
            }

            user_balance_list.append(current_currency)
        else:
            current_currency = {
                "currency_id": currency,
                "balance": result[0][3]
            }

            user_balance_list.append(current_currency)

    return {
        "user_id": user_id,
        "result": user_balance_list
    }

@app.get("/users/{user_id}/time")
async def get_user_time(user_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return

    user_data = result[0]
    
    available_user_time = 0
    # доступное время в секундах пишем сюда

    sql = "SELECT * FROM `user_products` WHERE `user_id`='"+ str(user_id) +"' AND `status`='active'"
    result = sql_query(sql)

    for product in result:
        # проходимся по списку активных пакетов пользователя
        user_product_id = product[0]
        # id пакета у пользователя в user_products
        product_id = product[2]
        # id пакета в products

        played_time = product[3]
        purchase_date = product[5]

        sql = "SELECT * FROM `products` WHERE `id`='" + str(product_id) + "'"
        product_result = sql_query(sql)

        if len(product_result) == 0:
            # если продукт с таким id не найден - пропускаем его 
            continue

        product_data = product_result[0]

        included_time = product_data[3]
        # время, включенное в пакет 
        life_time = product_data[4]
        # время жизни в секундах

        p_date_ts = dt.datetime.timestamp(purchase_date)
        now = dt.datetime.now()
        now_ts = dt.datetime.timestamp(now)
        # получаем timestamp, чтоб считать в секундах

        diff = now_ts - p_date_ts
        # кол-во секунд с момента покупки пакета

        if diff > life_time:
            # пакет истёк - обновляем БД и пропускаем 
            sql = "UPDATE `user_products` SET `status`='expired' WHERE `id`='" + str(user_product_id) + "'"
            sql_query(sql)
            
            continue

        expired_ts = p_date_ts + life_time
        # timestamp истечения пакета

        available_time = included_time - played_time
        # время пакета, которое не отыграно

        if available_time <= 0:
            # время пакета кончилось - обновляем БД и пропускаем
            sql = "UPDATE `user_products` SET `status`='expired' WHERE `id`='" + str(user_product_id) + "'"
            continue

        if (now_ts + available_time) > expired_ts:
            # если времени осталось больше, чем до конца жизни пакета...
            available_time = expired_ts - now_ts
            # получаем кол-во времени до истечения
        
        available_user_time = available_user_time + available_time

    # тут считаем доступное время по балансу
    usergroup_id = user_data[5]
    calculation_method = user_data[12]    

    sql = "SELECT * FROM `usergroups` WHERE `id`='" + str(usergroup_id) + "'"
    result = sql_query(sql)

    billing_profile_id = result[0][2]

    sql = "SELECT * FROM `billing_profiles` WHERE `id`='" + str(billing_profile_id) + "'"
    result = sql_query(sql)

    sheme = json.loads(result[0][1])
    #описание схемы биллинга 

    day_of_week = dt.datetime.today().weekday()
    # тут порядковый номер дня недели от 0 до 6 (пн-вс)

    is_exception = False
    # в эту переменную запишем, попадает-ли момент в исключения
    profile = sheme["default"]
    # сюда запишем описание профиля

    for exception in sheme["exсeptions"]:
        #сначала проверяем, не попадает-ли текущий момент в исключения

        if exception["day_of_week"] == day_of_week:
            #если день недели попал
            date_begin_str = "01-01-20 " + str(exception["time_from"]) + ":00"
            date_end_str = "01-01-20 " + str(exception["time_to"]) + ":00"
            # получаем в строке время, но чтоб каждая метка была на одну дату
            # нас интересует только время, поэтому дата должна быть одинаковая
            
            now = dt.datetime.now()
            curr_time_str = "01-01-20 " + now.strftime("%H:%M") + ":00"
            # получаем такую-же строку для текущего времени

            date_begin_ts = time.mktime(dt.datetime.strptime(date_begin_str, "%m-%d-%y %H:%M:%S").timetuple()) 
            curr_time_ts = time.mktime(dt.datetime.strptime(curr_time_str, "%m-%d-%y %H:%M:%S").timetuple()) 
            date_end_ts = time.mktime(dt.datetime.strptime(date_end_str, "%m-%d-%y %H:%M:%S").timetuple()) 

            if curr_time_ts > date_begin_ts and curr_time_ts < date_end_ts:
                # если текущая timestamp метка попадает в исключения - получаем профиль и закрываем цикл
                profile = exception["profile"]
                break

    is_actual_currency_found_in_profile = False
    # есть-ли выбранная валюта в профиле биллинга
    price_per_hour = 0
    # сюда запишем цену за час

    for currency in profile:
        if currency["currency_id"] ==  calculation_method:
            is_actual_currency_found_in_profile = True
            price_per_hour = currency["price"]
            break

    if(is_actual_currency_found_in_profile):
        # если выбранная валюта есть в списке биллинга - считаем, сколько времени осталось у человека
        sql = "SELECT * FROM `user_balance` WHERE `user_id`='" + str(user_id) + "' AND `currency_id`='" + str(calculation_method) + "'"
        result = sql_query(sql)

        user_currency_balance = 0

        if len(result) == 0:
            #кошелька в выбранной валюте нет - создаём
            sql = "INSERT INTO `user_balance`(`user_id`, `currency_id`, `balance`) VALUES ('" + str(user_id) + "','" + str(calculation_method) + "','0')"
            sql_query(sql)
        else:
            user_currency_balance = result[0][3]

        if user_currency_balance > 0:
            # если баланс не пустой - считаем, на сколько его хватит
            second_price = price_per_hour / 60 / 60

            available_time_for_balance = user_currency_balance / second_price

            available_user_time = available_user_time + available_time_for_balance
            # прибавляем полученное время к времени пакетов

    return {"result": available_user_time}                

@app.post("/users/create")
async def create_user(data: UserCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    username = data.username
    password = data.password
    name = data.name or ""
    surname = data.surname or ""
    email = data.email or ""
    phone = data.phone 
    city = data.city or ""
    country = data.country or ""
    address = data.adress or ""
    
    password_hash = hashlib.md5(password.encode())

    if(validate_phone(phone) == False):
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Invalid phone"
        }}

    if(validate_email(email) == False and email != ""):
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Invalid email"
        }}

    sql = "SELECT * FROM `users` WHERE `username`='" + str(username) +"' OR `phone`='" + str(phone) +"'"

    result = sql_query(sql)

    if(len(result) != 0):
        response.status_code = status.HTTP_409_CONFLICT
        return {"result": {
            "message": "Not unique username or phone"
        }}

    sql = "INSERT INTO `users`(`username`, `password_hash`, `name`, `surname`, `usergroup_id`, `avatar_id`, `email`, `phone`, `country`, `city`, `address`) VALUES ('" + str(username) + "','" + str(password_hash.hexdigest()) + "','" + str(name) + "','" + str(surname) + "','1','0','" + str(email) + "','" + str(phone) + "','" + str(country) + "','" + str(city) + "','" + str(address) + "')"

    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}

@app.get("/users/{username}/{password}/valid")
async def valid_user(username, password, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    password_hash = hashlib.md5(password.encode())

    sql = "SELECT * FROM `users` WHERE `username`='" + str(username) +"' AND `password_hash`='" + str(password_hash.hexdigest()) +"'"

    result = sql_query(sql)

    if(len(result) == 0):
        return {"result":{
            "status": "Failed",
            "message": "Incorrect username or password"
        }}
    else:
        return {"result":{
            "status": "Success",
            "user_id": result[0][0]
        }}


# методы products
@app.get("/products")
async def get_all_products(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `products`"
    result = sql_query(sql)

    products_list = []

    for product in result:
        curr_product = {
            "id": product[0],
            "name": product[1],
            "priority_level": product[2],
            "included_time": product[3],
            "lifetime": product[4],
            "available_options": json.loads(product[5]),
            "coast_sheme": json.loads(product[6])
        }

        products_list.append(curr_product)

    return {"result": products_list}

@app.post("/products/create")
async def create_billing_profile(data: ProductCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    name = data.name
    priority_level = data.priority_level
    included_time = data.included_time
    lifetime = data.lifetime
    available_options = data.available_options
    coast_sheme = data.coast_sheme

    if len(name) < 3:  
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Name must be longer 3 symbols"
        }}

    available_options = json.dumps(available_options)
    coast_sheme = json.dumps(coast_sheme)

    sql = "INSERT INTO `products`(`name`, `priority_level`, `included_time`, `lifetime`, `available_options`, `coast_sheme`) VALUES ('"+ str(name) +"','"+ str(priority_level) +"','"+ str(included_time) +"','"+ str(lifetime) +"','"+ str(available_options) +"','"+ str(coast_sheme) +"')"
    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}


# методы orders
@app.get("/orders")
async def get_all_orders(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `orders` ORDER BY `id` ASC"
    result = sql_query(sql)

    orders_list = []

    for order in result:
        current_order = {
            "id": order[0],
            "user_id": order[1],
            "product_id": order[2],
            "transaction_id": order[3],
            "date": order[4]
        }

        orders_list.append(current_order)

    return {"result": orders_list}

@app.post("/orders/{user_id}/{product_id}/{currency_id}/invoice")
async def order_product(user_id, product_id, currency_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `users` WHERE `user_id`='" + user_id + "'"
    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result": {
            "message": "User not found!"
        }}
    
    sql = "SELECT * FROM `products` WHERE `id`='" + product_id + "'"
    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result": {
            "message": "Product not found!"
        }}
    
    # проверили существование пользователя и пакетеа
    
    product_data = result[0]

    coast_sheme = json.loads(product_data[6])
    # загружаем схему цен

    product_coast = 0
    # цена на пакет будет записана сюда
    user_currency_balance = 0
    # баланс пользователя в выбранной валюте будет тут
    user_currency_balance_id = 0
    # id строки в БД, где записан баланс пользователя
    is_currency_available = False
    # сюда запишем статус доступности выбранной валюты...
    # ...для оплаты выбранного пакета

    for profile in coast_sheme["profile"]:
        # проверяем наличие выбранной валюты в профилях цен
        if str(profile["currency_id"]) == currency_id:
            # Если валюта существует - записываем цену и закрываем цикл
            product_coast = profile["price"]
            is_currency_available = True
            break

    if not is_currency_available:
        # Если валюта не нашлась в профилях - возвращаем ошибку
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"result": {
            "message": "Currency not available!"
        }}

    sql = "SELECT * FROM `user_balance` WHERE `user_id`='" + str(user_id) + "' AND `currency_id`='" + str(currency_id) + "'"

    result = sql_query(sql)
    # получили баланс пользователя в указанной валюте

    if(len(result) == 0):
        # Если валюта не существует - создаём её
        sql = "INSERT INTO `user_balance`(`user_id`, `currency_id`, `balance`) VALUES ('" + str(user_id) + "','" + str(currency_id) + "','0')"
        sql_query(sql)
        
        # при создании кошелька его баланс - 0
        user_currency_balance = 0
    else:
        user_currency_balance_id = result[0][0]
        user_currency_balance = result[0][3]

    user_currency_balance -= product_coast

    if(user_currency_balance < 0):
        # Если денег на балансе не достаточно - возвращаем ошибку
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"result":{
            "message":"Not enough money"
        }}

    sql = "UPDATE `user_balance` SET `balance`='" + str(user_currency_balance) + "' WHERE `id`='" + str(user_currency_balance_id) + "'"
    sql_query(sql)
    # обновляем баланс пользователя

    sql = "INSERT INTO `transactions`(`user_id`, `summ`, `currency_id`, `created_by_id`, `date`, `type`) VALUES ('" + str(user_id) + "','" + str(product_coast) + "','" + str(currency_id) + "','"+ str(veirify) +"',NOW(),'payment')"
    sql_query(sql)
    # Создаём транзакцию в БД

    sql = "SELECT * FROM `transactions` WHERE `user_id`='" + str(user_id) + "' AND `summ`='" + str(product_coast) + "' AND `type`='payment' AND `date` > NOW() - INTERVAL 1 MINUTE"
    result = sql_query(sql)
    # получаем id созданной транзакции
    transaction_id = result[0][0]
    
    sql = "INSERT INTO `user_products`(`user_id`, `product_id`, `played_time`, `status`, `purchase_date`, `activation_date`) VALUES ('" + str(user_id) + "','" + str(product_id) + "','0','await', NOW(),'0000-00-00 00:00:00')"
    sql_query(sql)
    # добавляем пакет пользователю

    sql = "INSERT INTO `orders`(`user_id`, `product_id`, `transaction_id`, `date`) VALUES ('" + str(user_id) + "','" + str(product_id) + "','" + str(transaction_id) + "', NOW())"
    sql_query(sql)
    # записываем заказ пользователя

    return


# методы usergroups

@app.get("/usergroups")
async def get_all_usergroups(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `usergroups`";
    result = sql_query(sql)
    
    usergroups_list = []

    for usergroup in result:
        current_usergroup = {
            "id": usergroup[0],
            "name": usergroup[1],
            "billing_profile_id": usergroup[2]
        }

        usergroups_list.append(current_usergroup)

    return {"result": usergroups_list}

@app.post("/usergroups/create")
async def create_billing_profile(data: UsergroupCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return  

    name = data.name
    billing_profile_id = data.billing_profile_id

    sql = "SELECT * FROM `billing_profiles` WHERE `id`='"+ str(billing_profile_id) +"'"
    result = sql_query(sql)

    if(len(name) < 3):
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Name must be longer 3 symbols"
        }}

    if(len(result) == 0):
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Billing profile not found"
        }}
    
    sql = "SELECT * FROM `usergroups` WHERE `name`='"+ str(name) +"'"
    result = sql_query(sql)

    if(len(result) != 0):
        response.status_code = status.HTTP_409_CONFLICT

        return {"result": {
            "message": "Name is not unique"
        }}

    sql = "INSERT INTO `usergroups`(`name`, `billing_profile_id`) VALUES ('" + str(name) + "','" + str(billing_profile_id) + "')"
    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}


# методы admins/*

@app.get("/admins")
async def get_all_admins(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `admins`";
    result = sql_query(sql)
    
    admins_list = []

    for admin in result:
        current_admin = {
            "id": admin[0],
            "username": admin[1],
            "rights_group": admin[3]
        }

        admins_list.append(current_admin)

    return {"result": admins_list}

@app.post("/admins/create")
async def create_admin(data: AdminCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    username = data.username
    password = data.password
    
    password_hash = hashlib.md5(password.encode())

    sql = "SELECT * FROM `admins` WHERE `username`='" + str(username) +"'"

    result = sql_query(sql)

    if(len(result) != 0):
        response.status_code = status.HTTP_409_CONFLICT
        return {"result": {
            "message": "Not unique username"
        }}

    sql = "INSERT INTO `admins`(`username`, `password_hash`, `rights_group_id`) VALUES ('" + str(username) + "','" + str(password_hash.hexdigest()) + "','0')"

    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}

@app.post("/admins/validate")
async def validate_admin(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    return {"result":{
            "status": "Success",
            "user_id": veirify
        }}


# методы hosts/*

@app.get("/hosts")
async def get_all_hosts(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    hosts_list = []

    sql = "SELECT * FROM `hosts`"
    result = sql_query(sql)

    for row in result:
        current_host = {
            "id": row[0],
            "name": row[1],
            "identifier": row[2],
            "player_id": row[3],
            "status": row[4]
        }

        hosts_list.append(current_host)
        
    return {"result": hosts_list}

@app.get("/hosts/{host_id}")
async def get_host_by_id(host_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `hosts` WHERE `id`='" + str(host_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
        
    host_data = {
        "id": result[0][0],
        "name": result[0][1],
        "identifier": result[0][2],
        "player_id": result[0][3],
        "status": result[0][4]
    }
        
    return {"result": host_data}

@app.get("/hosts/{host_identifier}/identifier")
async def get_host_by_id(host_identifier, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `hosts` WHERE `identifier`='" + str(host_identifier) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
        
    host_data = {
        "id": result[0][0],
        "name": result[0][1],
        "identifier": result[0][2],
        "player_id": result[0][3],
        "status": result[0][4]
    }
        
    return {"result": host_data}

@app.post("/hosts/create")
async def create_host(data: HostCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    name = data.name
    identifier = data.identifier

    sql = "SELECT * FROM `hosts` WHERE `name`='" + str(name) +"' OR `identifier`='" + str(identifier) + "'"

    result = sql_query(sql)

    if(len(result) != 0):
        response.status_code = status.HTTP_409_CONFLICT
        return {"result": {
            "message": "Not unique name or identifier"
        }}

    sql = "INSERT INTO `hosts`(`name`, `identifier`, `player_id`, `status`) VALUES ('" + str(name) + "','" + str(identifier) + "','0','disabled')"

    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}


# методы currency
@app.get("/currency")
async def get_all_currency(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `currency` ORDER BY `id` ASC"
    result = sql_query(sql)

    currency_list = []

    for currency in result:
        current_currency = {
            "id": currency[0],
            "name": currency[1],
            "symbol": currency[2]   
        }

        currency_list.append(current_currency)
    
    return {"result": currency_list}

@app.post("/currency/create")
async def create_currency(data: CurrencyCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    name = data.name
    symbol = data.symbol

    sql = "SELECT * FROM `currency` WHERE `name`='" + str(name) + "' OR `symbol`='" + str(symbol) + "'"
    result = sql_query(sql)

    if(len(result) > 0):
        response.status_code = status.HTTP_409_CONFLICT
        return {"result": {
            "message": "Not unique name or symbol"
        }}
    
    sql = "INSERT INTO `currency`(`name`, `symbol`) VALUES ('" + str(name) + "','" + str(symbol) + "')"
    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}


# методы transactions/*

@app.get("/transactions")
async def get_all_transaction(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    transactions_list = []

    sql = "SELECT * FROM `transactions`"
    result = sql_query(sql)

    for row in result:
        current_transaction = {
            "id": row[0],
            "user_id": row[1],
            "summ": row[2],
            "currency_id": row[3],
            "created_by_id": row[4],
            "date": row[5],
            "type": row[6]
        }

        transactions_list.append(current_transaction)
        
    return {"result": transactions_list}
    
@app.get("/transactions/{transaction_id}")
async def get_all_transaction(transaction_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    
    sql = "SELECT * FROM `transactions` WHERE `id`='" + str(transaction_id) + "'"
    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result":{
            "message": "Transaction not found"
        }}

    transaction_data = result[0]

    response = {
        "id": transaction_data[0],
        "user_id": transaction_data[1],
        "summ": transaction_data[2],
        "currency_id": transaction_data[3],
        "created_by_id": transaction_data[4],
        "date": transaction_data[5],
        "type": transaction_data[6]
    }

    return {"result": response}

@app.post("/transactions/create")
async def create_transaction(data: TransactionCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    user_id = data.user_id
    summ = data.summ
    currency_id = data.currency_id
    type = data.type 
    # deposit, payment или set

    if(summ < 0):
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"result":{
            "message": "Summ < 0"
        }}

    if(type != "deposit" and type != "payment" and type != "set"):
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"result":{
            "message": "Type must be deposit, payment or set"
        }}

    sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result":{
            "message": "User not found"
        }}
    
    sql = "SELECT * FROM `currency` WHERE `id`='" + str(currency_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result":{
            "message": "Currency not found"
        }}
    
    user_currency_balance_id = 0
    user_currency_balance = 0

    sql = "SELECT * FROM `user_balance` WHERE `user_id`='" + str(user_id) + "' AND `currency_id`='" + str(currency_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        sql = "INSERT INTO `user_balance`(`user_id`, `currency_id`, `balance`) VALUES ('" + str(user_id) + "','" + str(currency_id) + "','0')"
        sql_query(sql)

        user_currency_balance = 0
    else:
        user_currency_balance_id = result[0][0]
        user_currency_balance = result[0][3]

    if(type == "deposit"):
        user_currency_balance += summ

        sql = "UPDATE `user_balance` SET `balance`='" + str(user_currency_balance) + "' WHERE `id`='" + str(user_currency_balance_id) + "'"
        sql_query(sql)

        sql = "INSERT INTO `transactions`(`user_id`, `summ`, `currency_id`, `created_by_id`, `date`, `type`) VALUES ('" + str(user_id) + "','" + str(summ) + "','" + str(currency_id) + "','"+ str(veirify) +"',NOW(),'deposit')"
        sql_query(sql)
    
    if(type == "payment"):
        user_currency_balance -= summ

        if(user_currency_balance < 0):
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"result":{
                "message":"Not enough money"
            }}

        sql = "UPDATE `user_balance` SET `balance`='" + str(user_currency_balance) + "' WHERE `id`='" + str(user_currency_balance_id) + "'"
        sql_query(sql)

        sql = "INSERT INTO `transactions`(`user_id`, `summ`, `currency_id`, `created_by_id`, `date`, `type`) VALUES ('" + str(user_id) + "','" + str(summ) + "','" + str(currency_id) + "','"+ str(veirify) +"',NOW(),'payment')"
        sql_query(sql)

    if(type == "set"):
        user_currency_balance = summ

        sql = "UPDATE `user_balance` SET `balance`='" + str(user_currency_balance) + "' WHERE `id`='" + str(user_currency_balance_id) + "'"
        sql_query(sql)

        sql = "INSERT INTO `transactions`(`user_id`, `summ`, `currency_id`, `created_by_id`, `date`, `type`) VALUES ('" + str(user_id) + "','" + str(summ) + "','" + str(currency_id) + "','"+ str(veirify) +"',NOW(),'set')"
        sql_query(sql)

    response.status_code = status.HTTP_201_CREATED
    return


# методы reservations/*

@app.get("/reservations")
async def get_reservations(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    
    sql = "SELECT * FROM `reservations` ORDER BY `date_from` DESC LIMIT 100"
    result = sql_query(sql)

    reservations_list = []

    for reservation in result:
        current_reservation = {
            "id": reservation[0],
            "date_from": reservation[1],
            "date_to": reservation[2],
            "user_id": reservation[3],
            "host_id": reservation[4]
        }

        reservations_list.append(current_reservation)

    return {"result": reservations_list}
    # тут продолжить

@app.get("/reservations/nearest")
async def get_nearest_reservations(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    
    sql = "SELECT * FROM `reservations` WHERE (`date_from` > NOW()) AND `date_from` < NOW() + INTERVAL 24 HOUR"
    result = sql_query(sql)

    reservations_list = []

    for reservation in result:
        current_reservation = {
            "id": reservation[0],
            "date_from": reservation[1],
            "date_to": reservation[2],
            "user_id": reservation[3],
            "host_id": reservation[4]
        }

        reservations_list.append(current_reservation)

    return {"result": reservations_list}
    # тут продолжить


@app.post("/reservations/create")
async def create_reservation(data: ReservationCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    user_id = data.user_id
    host_id = data.host_id
    date_from = data.date_from
    date_to = data.date_to

    sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result":{
            "message": "User not found"
        }}

    sql = "SELECT * FROM `hosts` WHERE `id`='" + str(host_id) + "'"

    result = sql_query(sql)

    if(len(result) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"result":{
            "message": "Host not found"
        }}

    sql = "SELECT * FROM `reservations` WHERE ((`date_from`>='" + str(date_from) + "' AND `date_from`<='" + str(date_to) + "') OR (`date_to`>='" + str(date_from) + "' AND `date_to`<='" + str(date_to) + "') OR ('" + str(date_from) + "'>=`date_from` AND '" + str(date_from) + "'<=`date_to`) OR ('" + str(date_to) + "'>=`date_from` AND '" + str(date_to) + "'<=`date_to`)) AND `host_id`='" + str(host_id) + "'"

    result = sql_query(sql)

    if(len(result) != 0):
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"result":{
            "message": "Host is unavailable"
        }}

    sql = "INSERT INTO `reservations`(`date_from`, `date_to`, `user_id`, `host_id`) VALUES ('" + str(date_from) + "','" + str(date_to) + "','" + str(user_id) + "','" + str(host_id) + "')"

    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED
    return


# методы billing
@app.get("/billing")
async def get_billing_profiles(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    sql = "SELECT * FROM `billing_profiles`";
    result = sql_query(sql)
    
    profiles_list = []

    for profile in result:
        sheme = json.loads(profile[1])

        current_profile = {
            "id": profile[0],
            "sheme": sheme
        }

        profiles_list.append(current_profile)

    return {"result": profiles_list}

@app.post("/billing/create")
async def create_billing_profile(data: BillingProfile, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return  

    name = data.name
    default_profile = data.default
    exeptions_list = data.exeptions

    if len(name) < 3:  
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {"result": {
            "message": "Name must be longer 3 symbols"
        }}
    
    for profile in default_profile:
        try:
            if profile['currency_id'] == "" or profile['price'] == "":
                response.status_code = status.HTTP_400_BAD_REQUEST

                return {"result": {
                    "message": "Error in default profile data"
                }}
        except:
            response.status_code = status.HTTP_400_BAD_REQUEST

            return {"result": {
                "message": "Error in default profile data"
            }}

    for exception in exeptions_list:
        try:
            if exception['day_of_week'] == "" or exception['time_from'] == "" or exception['time_to'] == "":
                response.status_code = status.HTTP_400_BAD_REQUEST

                return {"result": {
                    "message": "Invalid exeption data"
                }}

            for profile in exception['profile']:
                if profile['currency_id'] == "" or profile['price'] == "":
                    response.status_code = status.HTTP_400_BAD_REQUEST

                    return {"result": {
                        "message": "Invalid exeption profile"
                    }}
                    
        except:
            response.status_code = status.HTTP_400_BAD_REQUEST

            return {"result": {
                    "message": "Invalid exeption data"
            }}

    obj = {
        "name":name,
        "default":default_profile,
        "exceptions":exeptions_list
    }

    json_data = json.dumps(obj)

    sql = "INSERT INTO `billing_profiles`(`sheme`) VALUES ('"+ json_data +"')"
    sql_query(sql)

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)