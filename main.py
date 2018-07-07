#!/usr/bin/python

import os
import requests
import json
import getpass
import time
import signal
import shutil

from FileHandler import FileHandler

#------------------ FIXED DATA ------------------
USER            = getpass.getuser()
MAIN_DIR        = "C:\\Users\\"+USER+"\\AppData\\Local\\AutoNewRelic",
CONFIG_FILE     = "config.json"
DRIVER_NAME     = 'geckodriver.exe'
DRIVER_DIR      = MAIN_DIR+'\\driver'
SCREENSHOTS_DIR = MAIN_DIR+'\\screenshots'
WAIT_TIME       = 10

def setup():
  global MAIN_DIR, CONFIG_FILE, DRIVER_NAME, DRIVER_DIR, SCREENSHOTS_DIR, DATA_FILE
  
  print('{0:-^60}\n{1:^60}\n{0:-^60}').format('','STARTING SETUP')
  print('\nIt looks like this is your first time running this program...\n Follow the steps to set it up!')  
  try:
    os.makedirs(DRIVER_DIR)
    os.makedirs(SCREENSHOTS_DIR)
  except:
    print('ERROR: There was a problem during the setup')
    print("To fix this run the '--setup' command on next startup to guarantee a clean setup")
  while(True):
    print("We have created the directories. Please place the '{0}' in the following directory: \n{1}".format(CONFIG_FILE, MAIN_DIR))
    raw_input('press ENTER when done...')
    if os.path.isfile(MAIN_DIR+'\\'+CONFIG_FILE):
      break
  while(True):
    print("Now insert the driver '{}' in the driver directory: \n{0}".format(DRIVER_NAME,DRIVER_DIR))
    raw_input('press ENTER when done...')
    if os.path.isfile(DRIVER_DIR+'\\'+DRIVER_NAME):
      break
  create_new_password()

      
def input_timeout(signum, frame):
  print("No option taken, running program normally...")

signal.signal(signal.SIGALRM, input_timeout)

def user_input(message):
  try:
    input = raw_input(message)
    return input
  except:
    return

def print_usage(message=""):
  print(message)
  usage_str = """
  
  These are the options:
  --help    
  --quit    
  --menu    
  --setup   
  --password
  --mode    
  --time    
  
  Choose only one at the time and try to put them in the required format:
  e.g. for 'HELP' either 'h', '-h' or '--help'
  
  To see more options go directly to the config file:
  {}
  
  However, be careful with the options you change there....
  Good luck!
  
  """.format(MAIN_DIR+CONFIG_FILE)

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
  global CONFIG_FILE
  
  payload = {
  'login[email]'      : username,
  'login[password]'   : password,
  'login[remember_me]': '0',
  'commit' : 'Sign in'
  }
  with open(CONFIG_FILE) as json_file:
    json_data = json.load(json_file, object_pairs_hook=to_str)
  
  url = 'https://'+ json_data['login_link'].__str__()
  
  with requests.session() as s:
    post = s.post(url, data=payload)
  return not "Unable to log in" in post.text
    
def check_options(option_taken):
  global CONFIG_FILE, MAIN_DIR

  if option.lower() in ('q', '-q', '--quit'):
    print("user decided to quit")
    exit(0)
  elif option.lower() in ('h', '-h', '--help'):
    print_usage("")
  elif option.lower() in ('m', '-m', '--menu'):
    menu_option = raw_input()
    check_options(menu_option)
  elif option.lower() in ('s', '-s', '--setup'):
    shutil.rmtree(MAIN_DIR)
  elif option.lower() in ('p', '-p', '--password'):
    while(True):
      username, password  = enter_credentials()
      login_successfull   = check_credentials(username, password)
      if not login_successfull and error_count == 3:
        print("You attempted the username and passwords too many times!. ")
        raw_input("I would recommend manually verifying your credentials\nthen restarting the program with option '-p' to change  the password. The link being used can be seen in the config file\n\nExiting Program...")
        exit(1)
      elif not login_successfull:
        print("Unable to log in. Please ensure that your email and password are correct.\n")
        continue
      break
    print("password changed successfully!")
  elif option.lower() in ('m', '-m', '--mode'):
    mode_str = """
    MODE SELECTED! There are three different modes that can be selected 
      
      TEST      : The best mode! This is a one-time run, easiest way to test!
                    The email is sent from you, to you, and with you as a copy.
                    Email is sent immediately after run, it does not check the time.
                    It does not include all the attachments a real message would.
      
      SIMULATION: A little closer to reality, but still nothing to worry about!
                    Email is sent from you to you again...
                    However it does check the time to send the email. 
                    AND it DOES includes all the attachments from all the links.
      
      REAL      : THE REAL DEAL! If you change this option the email will be sent to all the contacts in the 
                  'To' field and will copy to all the contacts in the 'Cc' field. Be careful!
                  
    --------------------------------------------------------------------------------------------------------
    You should be running now in Simulation Mode!
    If you would like to change it manually go to the {} file in the main directory:
    {}
    
    then go to section 2 and change it from SIMULATION to REAL:
          "_section2" : "---------------------- APP INFO ----------------------" ,
          "mode"                      : "_______________", <---- change this
    
    e.g. = 'TEST'
    
    Then run the program again when you're done... for safety reasons we will close after you press ENTER
    """.format(CONFIG_FILE, MAIN_DIR)
    raw_input(mode_str)
    print('Exiting....')
    time.sleep(1)
    exit(0)
  elif option.lower() in ('t', '-t', '--time'):
    time_str="""
    TIME SELECTED! This options shows you how to select the time that the email will be sent everyday.

      Note    : If the set time has already passed when the program is executed, the program 
                will send the email immediately.
      
      WARNING : If you decide to change this value, test it in SIMULATION mode before running it.
                Not all conditions for this program have been tested. If the set time is not 
                understood by the program, the email will be sent by default 'immediately'.
                  
    --------------------------------------------------------------------------------------------------------
    
    If you would like to change it manually go to the {} file in the main directory:
    {}
    
    then go to section 2 and change it from SIMULATION to REAL:
      "_section2" : "---------------------- APP INFO ----------------------" ,
      "send_email_time"                      : "_______________", <---- change this(specify time zone)
      
    e.g.  '18:00:00 AST'
      
    Then run the program again when you're done... for safety reasons we will close after you press ENTER
    """.format(CONFIG_FILE, MAIN_DIR)
    raw_input(time_str)
  else:
    # print_usage('option was not understood... printing usage...')
    print('continuing in normal mode now')
    
    
def enter_options():
  global WAIT_TIME
  print('{0:-^60}\n{1:^60}\n{0:-^60}').format('','OPTIONS')
  intro_str = """
  Program will start automatically in {} seconds... 
  
  However you can choose one of the following options:
      --help
      --quit          : To Quit
      --menu          : Keep menu open until ENTER is pressed
      --setup         : Delete everything and start over
      --password      : Change password
      --mode          : Change mode (simulation, real)
      --time          : Change send-email time
  """.format(WAIT_TIME)
  
  signal.alarm(WAIT_TIME)
  option = user_input(intro_str)
  signal.alarm(0)
  if option != None:
    check_options(option)
  
  
def create_new_password(message):
  global MAIN_DIR, encryption_key, block_size, DATA_FILE

  print(message)
  error_count = 0
  while(True):
    username, password  = enter_credentials()
    login_successfull   = check_credentials(username, password)
    if not login_successfull and error_count == 3:
      print("You attempted the username and passwords too many times!. ")
      raw_input("I would recommend manually verifying your credentials\nthen restarting the program with option '-p' to change  the password. The link being used can be seen in the config file\n\nExiting Program...")
      exit(1)
    elif not login_successfull:
      print("Unable to log in. Please ensure that your email and password are correct.\n")
      continue
    break
  print("login successfull!")
  
  file = FileHandler(filename= DATA_FILE, location=MAIN_DIR, block_size=block_size, key=encryption_key )
  file.username = username
  file.password = password
  if file.save() != -1:
    print('Username and password saved successfully!')
  else:
    print('For some reason.... username and password were not saved...')
    print('Exiting in 5 seconds...')
    time.sleep(5)
    exit(1)
    
  return username, password
  
if __name__=='__main__':
  global MAIN_DIR, DATA_FILE, CONFIG_FILE, DRIVER_NAME, DRIVER_DIR, SCREENSHOTS_DIR
  
  if os.name != 'nt':
    print("We apologize, this program was designed to run only on Windows machines. Exiting ...")
    exit(1)
  
  # Loading user options: user input and config file 'config.json'
  #--------------------------------------------------------------
  enter_options()
  if not os.path.isdir(MAIN_DIR): 
    setup()
  os.environ['PATH'] += os.pathsep + DRIVER_DIR+'\\'+DRIVER_NAME
  with open(CONFIG_FILE) as json_file:
    json_data = json.load(json_file, object_pairs_hook=to_str)
  
  mode            = json_data['mode'            ].__str__()
  email_body      = json_data['email_body'      ].__str__()
  new_encrypt_key = json_data['encryption_key'  ].__str__()
  new_block_size  = json_data['block_size'      ].__str__()
  login_link      = 'https:' + str(json_data['login_link' ])
  links           = [ str(i) for i in json_data['links']  ]
  
  # Update data file where password and username are stored
  #---------------------------------------------------------------
  file = FileHandler(filename= DATA_FILE, location=MAIN_DIR, block_size=block_size, key=encryption_key )
  username, password = file.load()
  file.key        = new_encrypt_key
  file.block_size = new_block_size
  file.username   = username
  file.password   = password
  file.write()
  send_email_time = json_data['send_email_time' ].__str__() if mode == 'REAL' or mode == 'SIMULATION' else 'NOW'
  if mode == 'REAL':
    to = json_data['to'].__str__()
    cc = json_data['cc'].__str__()
  else:
    to = username
    cc = username
  
  # Taking Screenshots
  #-------------------------------------------------------------
  print('{0:-^60}\n{1:^60}\n{0:-^60}').format('','STARTING PROGRAM')
  
  screenshots = []
  try:
    firefox = WebDriver(login_url=login_link, username=username, password=password )
    for i,link in enumerate(links):
      screenshot = SCREENSHOTS_DIR+'\\screenshot_{}.png'.format(i)
      screenshots.append(screenshot)
      firefox.printWebsite(link, screenshot)
  except Exception as e:
    print('ERROR while taking the website screenshots ')
    print(e)
  finally:
    firefox.close()
  
  # Creating Email
  #-------------------------------------------------------------
  try:
    email = Outlook(subject=subject, To=to, Cc=cc)
    email.addBody(email_body)
    for screenshot_path in screenshots:
      email.addAttachment(screenshot_path)
    email.send()
  except Exception as e:
    print('ERROR creating the email')
    print(e)
    
  