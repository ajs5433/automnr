#!/usr/bin/python

import os
import requests
import json
import getpass
import time
import signal
import shutil
import msvcrt

from FileHandler import FileHandler
from EmailHandler import Outlook
from WebDriver import WebDriver

#------------------ FONT FORMAT ------------------
SPECIAL_FONT_BLUE      = '\033[94m'
SPECIAL_FONT_GREEN     = '\033[92m'
SPECIAL_FONT_YELLOW    = '\033[93m'
SPECIAL_FONT_RED       = '\033[91m'
SPECIAL_FONT_BOLD      = '\033[1m'
SPECIAL_FONT_UNDERLINE = '\033[4m'
SPECIAL_FONT_END       = '\033[0m'

#------------------ FIXED DATA ------------------
USER            = getpass.getuser()
MAIN_DIR        = "{}{}{}".format("C:\\Users\\",USER,"\\AppData\\Local\\AutoNewRelic")
CONFIG_FILE     = "config.json"
DATA_FILE       = 'userdata'
DRIVER_NAME     = 'geckodriver.exe'
DRIVER_DIR      = "{}{}".format(MAIN_DIR ,'\\driver')
SCREENSHOTS_DIR = "{}{}".format(MAIN_DIR ,'\\screenshots')
WAIT_TIME       = 5.0

block_size      = 256
encryption_key  = 'newrelickey'

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
  return username, passwd

def check_credentials(username, password):
  global CONFIG_FILE
  
  payload = {
  'login[email]'      : username,
  'login[password]'   : password,
  'login[remember_me]': '0',
  'commit' : 'Sign in'
  }
  with open(CONFIG_FILE) as json_file:
    json_data = json.load(json_file)
  
  url = 'https://'+ json_data['login_link'].__str__()
  
  try:
    with requests.session() as s:
      post = s.post(url, data=payload)
  except Exception as e:
    string = """
    There was an error checking the login website. Please verify the config file is in the correct format:
    
    e.g.  www.google.com                GOOD
          https://www.google.com        WRONG
          
    However the error message was: {}
    """.format(e)
    print('There was ')
  return not "Unable to log in" in post.text

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

def manually_move_files(MAIN_DIR, CONFIG_FILE, DRIVER_DIR, DRIVER_NAME):
  global SPECIAL_FONT_BLUE, SPECIAL_FONT_GREEN,  SPECIAL_FONT_YELLOW, SPECIAL_FONT_RED, SPECIAL_FONT_BOLD, SPECIAL_FONT_UNDERLINE, SPECIAL_FONT_END
  bold_     = SPECIAL_FONT_BOLD
  end_bold  = SPECIAL_FONT_END  
  underline_= SPECIAL_FONT_UNDERLINE
  end_under = SPECIAL_FONT_END  
  while(True):
    print("\nPlease place the {bold_}'{CONFIG_FILE}'{end_bold} file in the following directory: \n{underline_}{MAIN_DIR}{end_under}\n".format(**locals()))
    raw_input('press ENTER when done...')
    if os.path.isfile(MAIN_DIR+'\\'+CONFIG_FILE):
      break
    print('The file was not there. Please make sure you have placed the correct file')
  while(True):
    print("\nNow insert the driver {bold_}'{DRIVER_NAME}'{end_bold} in the driver directory: \n{underline_}{DRIVER_DIR}{end_under}".format(**locals()))
    raw_input('press ENTER when done...')
    if os.path.isfile(DRIVER_DIR+'\\'+DRIVER_NAME):
      break
    print('The file was not there. Please make sure you have placed the correct file')
  
def move_setup_files(MAIN_DIR, CONFIG_FILE, DRIVER_DIR, DRIVER_NAME):
  try:
    shutil.copy(os.getcwd()+'\\'+CONFIG_FILE , MAIN_DIR+'\\'+CONFIG_FILE)
    shutil.copy(os.getcwd()+'\\'+DRIVER_NAME , DRIVER_DIR+'\\'+DRIVER_NAME)
  except Exception as e:
    print(e)
    print('There was an error moving the files automatically, we\'ll move them manually')
    if os.path.isfile(MAIN_DIR+'\\'+CONFIG_FILE):
      os.remove(MAIN_DIR+'\\'+CONFIG_FILE)
    if os.path.isfile(DRIVER_DIR+'\\'+DRIVER_NAME):
      os.remove(DRIVER_DIR+'\\'+DRIVER_NAME)
    manually_move_files(MAIN_DIR, CONFIG_FILE, DRIVER_DIR, DRIVER_NAME)
    
def setup(message, first_installation=False):
  global MAIN_DIR, CONFIG_FILE, DRIVER_NAME, DRIVER_DIR, SCREENSHOTS_DIR, DATA_FILE, block_size, encryption_key, \
         SPECIAL_FONT_BOLD, SPECIAL_FONT_END, SPECIAL_FONT_UNDERLINE
  
  print(message)  
  print('{0:-^60}\n{1:^60}\n{0:-^60}').format('','STARTING SETUP')
  
  while(True):
    input = 'y'
    if not first_installation:
      input = raw_input("We will first proceed to delete old isntallation files. Press Y- to confirm N - to Quit")
    if input.lower() in 'no' or input.lower() in 'quit':
      print('You decided to quit. Exiting... ')
    elif input.lower() in 'yes':
      if os.path.isdir(MAIN_DIR):
        shutil.rmtree(MAIN_DIR)
      break
    else:
      print('Did not get your input, please try again')  
  os.makedirs(DRIVER_DIR)
  os.makedirs(SCREENSHOTS_DIR)
  print 'We have created the directories!! ',
  move_setup_files(MAIN_DIR, CONFIG_FILE, DRIVER_DIR, DRIVER_NAME)
  
  with open(CONFIG_FILE) as json_file:
    json_data = json.load(json_file)
  encryption_key  = json_data['encryption_key'      ].__str__()
  block_size      = json_data['encryption_blocksize'].__int__()
  
  create_new_password("Now let's proceed to create a new passsword")


def print_usage(message=""):
  global MAIN_DIR, CONFIG_FILE
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
  
  """.format(MAIN_DIR+'\\'+CONFIG_FILE)

    
def check_options(option):
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
    setup("You selected the SETUP option!\n we'll begin now the setup process")
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
  
  print(intro_str)
  endtime = time.time() + WAIT_TIME
  option  = []
  
  while True:
    if msvcrt.kbhit():
      option.append(msvcrt.getche())
      if option[-1] == '\r':
        option = ''.join(option)
        break
      time.sleep(0.1)
    else:
      if time.time() > endtime:
        print('No option selected')
        option = None
        break
  if option != None:
    check_options(option)
  
  
if __name__=='__main__':
  # global MAIN_DIR, DATA_FILE, CONFIG_FILE, DRIVER_NAME, DRIVER_DIR, SCREENSHOTS_DIR
  if os.name != 'nt':
    print("We apologize, this program was designed to run only on Windows machines. Exiting ...")
    exit(1)
  os.system('cls')
  
  # Loading user options: user input and config file 'config.json'
  #--------------------------------------------------------------
  if not os.path.isdir(MAIN_DIR):
    print(MAIN_DIR)
    setup('\nIt looks like this is your first time running this program...\n Follow the steps to set it up!', first_installation=True)
  if not os.path.isfile(MAIN_DIR+'\\'+DATA_FILE):
    print(MAIN_DIR+'\\'+DATA_FILE)
    setup('\nIt looks like this is your first time running this program...\n Follow the steps to set it up!', first_installation=True)
  if not os.path.isfile(DRIVER_DIR+'\\'+DRIVER_NAME): 
    print(DRIVER_DIR+'\\'+DRIVER_NAME)
    setup('\nIt looks like this is your first time running this program...\n Follow the steps to set it up!', first_installation=True)
  os.environ['PATH'] += os.pathsep + DRIVER_DIR+'\\'+DRIVER_NAME
  enter_options()
  with open(CONFIG_FILE) as json_file:
    json_data = json.load(json_file)
  
  mode            = json_data['mode'                ].__str__()
  email_body      = json_data['email_body'          ].__str__()
  subject         = json_data['subject'             ].__str__()
  login_link      = 'https://' + str(json_data['login_link' ])
  links           = [ str(i) for i in json_data['links']  ]
  
  # Update data file where password and username are stored
  #---------------------------------------------------------------
  file = FileHandler(filename= DATA_FILE, location=MAIN_DIR, block_size=block_size, key=encryption_key )
  username,password = file.load()
  """
  file.key        = new_encrypt_key
  file.block_size = new_block_size
  file.username   = username
  file.password   = password
  file.write()
  """
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
    if firefox is not None:
      firefox.close()
  
  # Creating Email
  #-------------------------------------------------------------
  try:
    email = Outlook(subject=subject, to=to, cc=cc)
    email.addBody(email_body)
    for screenshot_path in screenshots:
      email.addAttachment(screenshot_path)
    email.send()
  except Exception as e:
    print('ERROR creating the email')
    print(e)
    
  