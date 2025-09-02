import bcrypt
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import BasePasswordHasher


class BcryptPasswordHasher(BasePasswordHasher):
    algorithm = 'bcrypt_custom'

    @staticmethod
    def _hash_password(password: str) -> str:
        if not password:
            raise ValidationError("Password cannot be empty")

        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        return hashed_password.decode('utf-8')

    
    @staticmethod
    def _verify_password(password: str, hashed_password: str) -> bool:
        if not password or not hashed_password:
            return False

        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except ValueError:
            return False

    def encode(self, password, salt=None):
        hashed_password = self._hash_password(password)
        return f'{self.algorithm}${hashed_password}'
    
    def verify(self, password, encoded):
        algorithm, hashed_password = encoded.split('$', 1)

        if algorithm != self.algorithm:
            return False
        
        return self._verify_password(password, hashed_password)
    
    def safe_summary(self, encoded):
        algorithm, hashed_password = encoded.split('$', 1)
        return {'algorithm': algorithm, 'hash': hashed_password[:6] + '...'}

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        pass


        

        

        


    
       


        
        




 
        


