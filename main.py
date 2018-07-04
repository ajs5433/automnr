#!/usr/bin/python

import os
import optparse
import requests

from FileHandler import FileHandler


#--------------------------------------------------------------------------------
#                                   DATA                                         
#--------------------------------------------------------------------------------

# file data
LOCATION    = ""
FILENAME    = "nrr_data"

# encryption data
KEY         = "newrelicexec"
BLOCK_SIZE  = 256

# website data
URL     =  'https://login.newrelic.com/login'

#--------------------------------------------------------------------------------

def enter_credentials():
  while(True):
    username  = raw_input("Please enter your newrelic username: ")
    username_ = raw_input("To verify, please re-enter username: ")
    passwd    = getpass.getpass("Enter your password: ")
    passwd_   = getpass.getpass("Re-enter password: ")
    
    if not username == username_:
      print("Usernames did not match, please try again")
      continue
    
    if not passwd == passwd_ :
      print("Passwords did not match, please try again")
      continue
    break
  return username, password
  
def check_credentials(username, password):
  payload = {
  'login[email]'      : username,
  'login[password]'   : password,
  'login[remember_me]': '0',
  'commit' : 'Sign in'
  }
  with requests.session() as s:
    post = s.post(URL, data=payload)
  return not "Unable to log in" in post.text

def create_new_password(message):
  print(message)
  error_count = 0
  while(True):
    username, password  = enter_credentials()
    login_successfull   = check_credentials(username, password)
    
    if not login_successfull and error_count == 3:
      print("You attempted the username and passwords too many times!. Exiting Program... ")
      exit(1)
    elif not login_successfull:
      print("Unable to log in. Please ensure that your email and password are correct.\n")
      continue
    break
  
if __name__=='__main__':

  parser = optparse.OptionParser(usage=" ")
  parser.add_option("-p", "--passwd", dest="changepasswd", type='bool', 
                    help=("This option is used to change the password [default: %default]"))
                    
  parser.set_defaults(changepasswd=False)
  opts, args = parser.parse_args()
  
  if os.name != 'nt':
    print("We apologize, this program was designed to run only on Windows machines. Exiting ...")
    exit(1)
  
  file = LOCATION + FILENAME
  if not os.path.isfile(file): 
    create_new_password("It looks like you have never set up your account\n")
  elif (opts.changepasswd==True):
    create_new_password("You chose the create_new_password option!\n")
      
  
  