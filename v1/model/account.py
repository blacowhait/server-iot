from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import Account_DB
import bcrypt
from hashlib import sha256

# ------------------------ Schema


class AccountBase(BaseModel):
    username: str
    password: str
    email: str
    isadmin: bool
    token: str

# ------------------------ Class

class Account():
    username : str
    password: str
    email: str
    isadmin: bool
    token: str

    # class Config:
    #     orm_mode = True

    def create(uname: str, eml: str, paswd: str, tokn: str, db: Session):
        salt = bcrypt.gensalt()
        # hashed = bcrypt.hashpw(paswd.encode(), salt)
        hashed = sha256(pswd.encode()).hexdigest()
        print(hashed)
        akun = Account_DB(
            username = uname,
            password = hashed.decode(),
            email = eml,
            isadmin = False,
            token = tokn,
            # activated = True
        )
        db.add(akun)
        db.commit()
        db.refresh(akun)
        db.close()
        return True
    
    def update(eml: str, paswd: str, db: Session):
        acc = db.query(Account_DB).filter(Account_DB.email == eml).first()
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(paswd.encode(), salt)
        acc.password = hashed.decode()
        db.commit()
        db.refresh(acc)
        db.close()
        return True
    
    def update_byself(eml: str, old: str, pswd: str, db: Session):
        acc = db.query(Account_DB).filter(Account_DB.email == eml).first()
        if acc:
            if bcrypt.checkpw(old.encode(), acc.password.encode()):
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(pswd.encode(), salt)
                acc.password = hashed.decode()
                db.commit()
                db.refresh(acc)
                db.close()
                return True
            else:
                return False
        else:
            return False

    def check_token(email: str, token: str, db: Session):
        acc = db.query(Account_DB).filter(Account_DB.email == email).first()
        if acc:
            if token == acc.token:
                acc.token = 'Done'
                # acc.activated = True
                db.commit()
                db.refresh(acc)
                db.close()
                return True
            else:
                return False
        else:
            return False

    def get_user(email: str, db:Session):
        acc = db.query(Account_DB).filter(Account_DB.email == email).first()
        db.close()
        return acc
    
    def get_all_user(db:Session):
        acc = db.query(Account_DB).order_by('id').all()
        db.close()
        return acc

    def is_exist(eml: str, db: Session):
        exist = db.query(Account_DB).filter(Account_DB.email == eml).first()
        db.close()
        if not exist:
            return False
        return True

    def check_pass(eml: str, pswd: str, db: Session):
        acc = db.query(Account_DB).filter(Account_DB.email == eml).first()
        db.close()
        enc_password = sha256(pswd.encode()).hexdigest()
        # if bcrypt.checkpw(pswd.encode(), acc.password.encode()):
        if enc_password == acc.password:
            return True
        else:
            return False