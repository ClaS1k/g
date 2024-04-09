# тут лежат функции валидации номера телефона и почты

import re
import config
from sql import *


def veirify_admin(username, password_hash):
    # валидация логина и пароля админа 
   
    sql = "SELECT * FROM `admins` WHERE `username`='" + str(username) +"' AND `password_hash`='" + str(password_hash) +"'"

    result = sql_query(sql)

    if(len(result) == 0):
        return False
    else:
        return result[0][0]


def validate_phone(phone):
    pattern = "^(\+7|8)[\- ]?\(?\d{3}\)?[\- ]?\d{3}[\- ]?\d{2}[\- ]?\d{2}$"

    if re.match(pattern, phone):
        return True
    else:
        return False

def validate_email(email):
    #validate email with regexp
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email):
        return True
    else:
        return False