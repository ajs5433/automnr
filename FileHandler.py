#!/usr/bin/python
"""
# -*- coding: ascii -*-
"""
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):
    """
    Encrypts and decrypts binary data
    
    Code obtained from: 
    https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
    """
    def __init__(self, key, block_size): 
        self.bs = block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class FileHandler(object):

  def __init__(self, filename="data", location="", block_size=128, key='58'):
    self.__filename   = filename
    self.__location   = location
    self.__username   = None
    self.__password   = None
    
    self.__crypto     = AESCipher(key, block_size)
    self.__block_size = block_size                      # max memory block size 
    self.__key        = key                             # Unique ID to decrypt the password
    self.__codec      = '*****'                           # separator field between username and password
    
  @property
  def username(self):
    return self.__username
  
  @username.setter
  def username(self, username):
    self.__username = str(username)
  
  @property
  def password(self):
    return self.__password
  
  @password.setter
  def password(self, password):
    self.__password = str(password)
  
  @property
  def block_size(self):
    return self.__block_size
  
  @block_size.setter
  def block_size(self, block_size):
    self.__block_size = str(block_size)
    
  @property
  def key(self):
    return self.__key
  
  @key.setter
  def key(self, key):
    self.__key = str(key)
  
  def write(self):
    """
    Writes data as bytes in the provided location and returns -1 if an error is found.
    """
    if not self.__filename and not self.__location:
      return -1
    try:
      full_path         = self.__location+self.__filename
      
      usr_pass   = "{}{}{}".format(self.__username,self.__codec,self.__password)
      data = self.__crypto.encrypt(usr_pass)
      
      with open(full_path, 'wb') as out_file:
        out_file.write(data)
        
    except Exception as e:
      print(e)
      return -1
  
  def load(self):
    """
    Loads the file and returns -1 if there is an error such as no file found
    """
    full_path = self.__location + self.__filename
    data = -1
    
    try:
      with open(full_path, 'rb') as in_file:
        encrypted_data = in_file.read()
        data = self.__crypto.decrypt(encrypted_data)
        
    except Exception as e:
      print(e)
    
    return str(data).split(self.__codec)
    #return str(data)
    
  def clear(self):
    pass
  
  
if __name__=='__main__':
  fh = FileHandler()
  ac = AESCipher('5', '100')