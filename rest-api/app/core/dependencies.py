from app.core.database import get_session
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


# region db


def get_db():
    sess = get_session()
    db: Session = sess()
    try:
        yield db
    finally:
        db.close()


# endregion

# region password

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token")
alternate_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token", auto_error=False)

# endregion
