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

from models import UserCreate, AdminCreate
from validate import *

app = FastAPI()
security = HTTPBasic()


#методы users/*

@app.get("/users")
async def get_all_users(response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    users_list = []

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE 1"

        cursor.execute(sql)

        result = cursor.fetchall()

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
                "sity": row[10],
                "adress": row[11],
            }

            users_list.append(current_user)
        
        return {"result": users_list}

@app.get("/users/{user_id}")
async def get_user_by_id(user_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

        cursor.execute(sql)

        result = cursor.fetchall()

        if(cursor.rowcount == 0):
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
            "sity": result[0][10],
            "adress": result[0][11],
        }
        
        return {"result": user_data}

@app.get("/users/{username}/username")
async def get_user_by_username(username, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `username`='" + str(username) + "'"

        cursor.execute(sql)

        result = cursor.fetchall()

        if(cursor.rowcount == 0):
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
            "sity": result[0][10],
            "adress": result[0][11],
        }
        
        return {"result": user_data}

@app.get("/users/{user_id}/balance")
async def get_user_balance(user_id, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `user_id`='" + str(user_id) + "'"

        cursor.execute(sql)

        result = cursor.fetchall()

        if(cursor.rowcount == 0):
            response.status_code = status.HTTP_404_NOT_FOUND
            return
    
    currency_list = []

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `currency`"

        cursor.execute(sql)

        result = cursor.fetchall()

        for row in result:
            currency_list.append(row[0])
    
    user_balance_list = []

    for currency in currency_list:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `user_balance` WHERE `user_id`='" + str(user_id) + "' AND `currency_id`='" + str(currency) + "'"

            cursor.execute(sql)

            result = cursor.fetchall()

            if(cursor.rowcount == 0):
                sql = "INSERT INTO `user_balance`(`user_id`, `currency_id`, `balance`) VALUES ('" + str(user_id) + "','" + str(currency) + "','0')"

                cursor.execute(sql)
                connection.commit()

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
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

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
    adress = data.adress or ""
    
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

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `username`='" + str(username) +"' OR `phone`='" + str(phone) +"'"

        cursor.execute(sql)

        cursor.fetchall()

        if(cursor.rowcount != 0):
            response.status_code = status.HTTP_409_CONFLICT
            return {"result": {
                "message": "Not unique username or phone"
            }}

    with connection.cursor() as cursor:
        sql = "INSERT INTO `users`(`username`, `password_hash`, `name`, `surname`, `usergroup_id`, `avatar_id`, `email`, `phone`, `country`, `sity`, `adress`) VALUES ('" + str(username) + "','" + str(password_hash.hexdigest()) + "','" + str(name) + "','" + str(surname) + "','0','0','" + str(email) + "','" + str(phone) + "','" + str(country) + "','" + str(city) + "','" + str(adress) + "')"

        cursor.execute(sql)
        connection.commit()

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}

@app.get("/users/{username}/{password}/valid")
async def valid_user(username, password, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

    admin_username = credentials.username
    admin_password_hash = hashlib.md5(credentials.password.encode())

    veirify = veirify_admin(admin_username, admin_password_hash.hexdigest())
    #тут будет лежать id админа, создавшего запрос

    if(veirify == False):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    password_hash = hashlib.md5(password.encode())

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `username`='" + str(username) +"' AND `password_hash`='" + str(password_hash.hexdigest()) +"'"

        cursor.execute(sql)

        result = cursor.fetchall()

        if(cursor.rowcount == 0):
            return {"result":{
                "status": "Failed",
                "message": "Incorrect username or password"
            }}
        else:
            return {"result":{
                "status": "Success",
                "user_id": result[0][0]
            }}


#методы admins/*

@app.post("/admins/create")
async def create_admin(data: AdminCreate, response: Response,  credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    connection = mysql.connector.connect(user = config.MYSQL_LOGIN, password = config.MYSQL_PASSWORD, host = config.MYSQL_HOST, port='3306', database='gizmokiller')

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

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `admins` WHERE `username`='" + str(username) +"'"

        cursor.execute(sql)

        cursor.fetchall()

        if(cursor.rowcount != 0):
            response.status_code = status.HTTP_409_CONFLICT
            return {"result": {
                "message": "Not unique username"
            }}

    with connection.cursor() as cursor:
        sql = "INSERT INTO `admins`(`username`, `password_hash`, `rights_group_id`) VALUES ('" + str(username) + "','" + str(password_hash.hexdigest()) + "','0')"

        cursor.execute(sql)
        connection.commit()

    response.status_code = status.HTTP_201_CREATED

    return {"result": {
        "message": "Success creation"
    }}

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)