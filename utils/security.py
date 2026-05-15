from passlib.context import CryptContext

#第一个参数是加密算法，第二个参数新旧加密算法自动兼容
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_password(password:str):
    return pwd_context.hash(password)

#验证password通过pwd_context加密后是否与hashed_password一致
def verify_password(password:str,hashed_password:str):
    return pwd_context.verify(password,hashed_password)
