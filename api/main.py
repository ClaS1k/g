import json
import requests
import time
import mysql
import uvicorn
import hashlib

import config

from fastapi import FastAPI, Depends, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from typing import Annotated

from mysql import connector

from models import UserCreate, AdminCreate, HostCreate, TransactionCreate, ReservationCreate
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
    address = data.address or ""
    
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

    sql = "INSERT INTO `users`(`username`, `password_hash`, `name`, `surname`, `usergroup_id`, `avatar_id`, `email`, `phone`, `country`, `city`, `address`) VALUES ('" + str(username) + "','" + str(password_hash.hexdigest()) + "','" + str(name) + "','" + str(surname) + "','0','0','" + str(email) + "','" + str(phone) + "','" + str(country) + "','" + str(city) + "','" + str(address) + "')"

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


# методы admins/*

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
        sql = "INSERT INTO `user_balance`(`user_id`, `currency_id`, `balance`) VALUES ('" + str(user_id) + "','" + str(currency) + "','0')"
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


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)