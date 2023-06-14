from passlib.context import CryptContext
from config import ENCRYPTION_KEY
from cryptography.fernet import Fernet

SECRET_KEY = '4cfbd1107dc91e5d8b0c1b988b0808499258ae2c8e3336f6aa225e1c122ffa0a'
ALGORITHM = "HS256"


class HasherClass:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.TokenGenerate = CryptContext(schemes=['des_crypt'], deprecated='auto')

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def GetToken(self, HashedPassword: str) -> str:
        return self.TokenGenerate.hash(HashedPassword)


class EncryptionClass:
    def __init__(self):
        self.cipher_suite = Fernet(ENCRYPTION_KEY)

    def decrypt_qrinfo(self, to_decrypt):
        return self.cipher_suite.decrypt(to_decrypt).decode('utf-8')
