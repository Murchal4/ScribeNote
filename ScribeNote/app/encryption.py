from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class EncryptionHandler:
    def __init__(self):
        self.salt = b'secure_notes_salt_value'  # In production, this should be randomly generated and stored securely
    
    def _get_key_from_password(self, password):
        """Derive a key from the password using PBKDF2"""
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, content, password):
        """Encrypt content using the provided password"""
        if not content:
            return ""
            
        key = self._get_key_from_password(password)
        f = Fernet(key)
        
        encrypted_data = f.encrypt(content.encode('utf-8'))
        return encrypted_data.decode('utf-8')
    
    def decrypt(self, encrypted_content, password):
        """Decrypt content using the provided password"""
        if not encrypted_content:
            return ""
            
        key = self._get_key_from_password(password)
        f = Fernet(key)
        
        decrypted_data = f.decrypt(encrypted_content.encode('utf-8'))
        return decrypted_data.decode('utf-8')
