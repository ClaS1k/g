# тут лежат функции валидации номера телефона и почты
import re

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