#!/usr/bin/python

import os
import requests
import json
import getpass
import time
import signal
import shutil
import msvcrt
import datetime
import Help

from time import strftime
from PIL import Image
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


with open(CONFIG_FILE) as json_file:
  json_data = json.load(json_file)
  WAIT_TIME = json_data['menu_wait_time'].__int__()

verbose         = False
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
  global MAIN_DIR, CONFIG_FILE, DRIVER_NAME, DRIVER_DIR, SCREENSHOTS_DIR, DATA_FILE, block_size, encryption_key
  
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
  --verbose
  --setup   
  --password 
  
  Choose only one at the time and try to put them in the required format:
  e.g. for 'HELP' either 'h', '-h' or '--help'
  
  To see modify options go directly to the config file:
  {}
  
  if you want help on a specific option you can type help and the option:
  e.g. '--help mode'
  
  However, be careful with the options you change there....
  Good luck!
  
  """.format(MAIN_DIR+'\\'+CONFIG_FILE)
  print(usage_str)
    
def check_options(options):
  global CONFIG_FILE, MAIN_DIR, verbose
  
  option = options.lower().split(' ')[0].strip()
  
  if option in('q', '-q', '--quit'):
    print("user decided to quit")
    exit(0)
  elif option in('h', '-h', '--help'):
    print('{0:-^60}'.format(''))
    if len(options.split(' ')) > 1:
      Help.printoption(options)
    else:
      print_usage("You have pressed Help!")
      Help.printoption(raw_input('what do you need help with? '))
    raw_input('Press ENTER to continue...')
  elif option in ('m', '-m', '--menu'):
    menu_option = raw_input()
    check_options(menu_option)
  elif option in ('s', '-s', '--setup'):
    setup("You selected the SETUP option!\n we'll begin now the setup process")
  elif option in ('v', '-v', '--verbose'):
    verbose = True
    print('verbose ON')
  elif option in ('p', '-p', '--password'):
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
  else:
    # print_usage('option was not understood... printing usage...')
    print('continuing in normal mode now ')
    
    
def enter_options():
  global WAIT_TIME
  print('{0:-^60}\n{1:^60}\n{0:-^60}').format('','OPTIONS')
  intro_str = """
  Program will start automatically in {} seconds... 
  
  However you can choose one of the following options:
      --help
      --quit          : To Quit
      --menu          : Keep menu open until ENTER is pressed
      --verbose       : To print all the steps
      --setup         : Delete everything and start over
      --password      : Change password
  """.format(WAIT_TIME)
  
  print(intro_str)
  endtime = time.time() + WAIT_TIME
  option  = []
  
  while True:
    if msvcrt.kbhit():
      option.append(msvcrt.getche())
      if option[-1] == '\x08':
        option = option[:-2]
      elif option[-1] == '\r':
        option = ''.join(option)
        break
      time.sleep(0.1)
    else:
      if time.time() > endtime:
        print('No option selected')
        option = None
        break
  if option != None:
    check_options(option.strip())
  
def print_total_elapsed_time_str(seconds):  
  seconds = int(seconds)
  print 'total elapsed time: ',
  if seconds > 3600:
    hours,seconds     = divmod(seconds,3600)
    minutes,seconds   = divmod(seconds,60)
    hour_str = 'hrs' if (hours>1) else 'hr'
    print '{} {} '.format(hours, hour_str),
  if seconds > 60:
    minutes,seconds   = divmod(seconds,60)
    minute_str ='mins' if (minutes>1) else 'min'
    print '{} {} '.format(minutes, minute_str),
  second_str ='secs' if (seconds>1) else 'sec'
  print '{} {} '.format(seconds, second_str)
  
def print_total_elapsed_time(seconds): 
  seconds = int(seconds)
  print 'total elapsed time: ',
  hours, minutes = (0,0)
  if seconds >= 86400:
   days,seconds = divmod(seconds,86400)
   print '{}d '.format(days),
  if seconds >= 3600:
    hours,seconds     = divmod(seconds,3600)
  if seconds >= 60:
    minutes,seconds   = divmod(seconds,60)
  print '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)
  
  
def crop_image(path, x1, y1, x2, y2):
  image = Image.open(path)
  area  = (x1,y1,x2,y2)
  cropped_image = image.crop(area)
  cropped_image.save(path)
  image.close()
  cropped_image.close()
  
if __name__=='__main__':
  # global MAIN_DIR, DATA_FILE, CONFIG_FILE, DRIVER_NAME, DRIVER_DIR, SCREENSHOTS_DIR
  if os.name != 'nt':
    print("We apologize, this program was designed to run only on Windows machines. Exiting ...")
    exit(1)
  os.system('cls')
  
  # Setup main config files and file folders and add directory to PATH
  #--------------------------------------------------------------
  if not os.path.isdir(MAIN_DIR) or not os.path.isfile(MAIN_DIR+'\\'+DATA_FILE) or not os.path.isfile(DRIVER_DIR+'\\'+DRIVER_NAME):
    setup('\nIt looks like this is your first time running this program...\n Follow the steps to set it up!', first_installation=True)

  if not os.pathsep + DRIVER_DIR+'\\'+DRIVER_NAME in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + DRIVER_DIR+'\\'+DRIVER_NAME
  enter_options()
  with open(CONFIG_FILE) as json_file:
    json_data = json.load(json_file)
  
  if verbose: print('Loading config data...')
  # loading user config data
  mode            = json_data['mode'                ].__str__()
  email_body      = json_data['email_body'          ].__str__()
  subject         = json_data['subject'             ].__str__()
  encryption_key  = json_data['encryption_key'      ].__str__()
  save_as_name    = json_data['save_images_as'      ].__str__()
  block_size      = json_data['encryption_blocksize'].__int__()
  page_load_delay = json_data['page_load_delay'     ].__int__()                         # the browser will wait for ELEMENT X to load for at least DELAY seconds
  crop_x1         = json_data['crop_x1'             ].__int__()
  crop_x2         = json_data['crop_x2'             ].__int__()
  crop_y1         = json_data['crop_y1'             ].__int__()
  crop_y2         = json_data['crop_y2'             ].__int__()
  send_email      = json_data['send_email'          ].__str__()
  send_email_time = json_data['send_email_time'     ].__str__()
  page_load_delay_element_id  = json_data['page_load_delay_element_id'].__str__()        # this is the ELEMENT X ID
  login_link      = 'https://' + str(json_data['login_link' ])
  links           = [ str(i) for i in json_data['links']  ]
  
  # Update data file where password and username are stored
  #---------------------------------------------------------------
  file = FileHandler(filename= DATA_FILE, location=MAIN_DIR, block_size=block_size, key=encryption_key )
  username,password = file.load()
  
  send_email_time = json_data['send_email_time' ].__str__() if mode == 'REAL' or mode == 'SIMULATION' else 'NOW'
  if mode == 'REAL':
    if verbose: print('REAL mode active, adding real receipients...')
    to = json_data['to'].__str__()
    cc = json_data['cc'].__str__()
  else:
    to = username
    cc = username
  
  # Taking Screenshots
  #-------------------------------------------------------------
  print('{0:-^60}\n{1:^60}\n{0:-^60}').format('','STARTING PROGRAM')
  start_time = time.time()
  
  print('Start time: \t{}'.format(datetime.datetime.now().strftime('%m/%d/%y %I:%M:%S %p')))
  
  #delete old saved images and then take new ones
  if verbose: print('Deleting old screenshots')
  screenshots = []
  filelist    = [ f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith(".png") ]
  for file in filelist:
    os.remove(os.path.join(SCREENSHOTS_DIR, file))
  try:
    if verbose: print('Opening Firefox and logging in')
    firefox = WebDriver(login_url=login_link, username=username, password=password )
    firefox.click24hrs(links[0])
    
    # the following for loops do exactly the same
    # separated to avoid asking if on every loop
    if verbose:
      for i,link in enumerate(links):
        if mode=='TEST' and i >=3 :
            break;
        print('\ttaking screenshot {}'.format(i+1))
        screenshot = SCREENSHOTS_DIR+'\\{}{}.png'.format(save_as_name,i+1)
        screenshots.append(screenshot)
        firefox.printWebsite(link, screenshot, delay =page_load_delay,element_id=page_load_delay_element_id )
    else:
      for i,link in enumerate(links):
        if mode=='TEST' and i >=3 :
          break;
        screenshot = SCREENSHOTS_DIR+'\\{}{}.png'.format(save_as_name,i+1)
        screenshots.append(screenshot)
        firefox.printWebsite(link, screenshot, delay =page_load_delay,element_id=page_load_delay_element_id )
        
  except Exception as e:
    print('ERROR while taking the website screenshots ')
    print(e)
  finally:
    if firefox is not None:
      #raw_input('waiting to close firefox')
      firefox.close()
  
  # Crop Image
  if verbose: print('Cropping Images:')
  if verbose:
    if screenshots: 
      image = Image.open(screenshots[0])
      width, height = image.size
      del image
      print('\tImages original size {}x{}'.format(width, height))
  if verbose:
    for i,image_full_path in enumerate(screenshots):
      print('\tcropping image {}'.format(i+1))
      crop_image(image_full_path, crop_x1, crop_y1, crop_x2, crop_y2)
  else:
    for image_full_path in screenshots:
      crop_image(image_full_path, crop_x1, crop_y1, crop_x2, crop_y2)
      
  # Creating Email
  #------------------------------------------------------------
  if verbose: print('Creating Email:')
  current_date_str  = datetime.datetime.now().strftime('%m/%d/%y')
  subject = '{} {}'.format(subject, current_date_str)
  
  current_time = lambda : datetime.datetime.now().strftime('%H:%M:%S')
  
  if verbose:
    try:
      email = Outlook(subject=subject, to=to, cc=cc)
      email.addBody(email_body)
      for i,screenshot_path in enumerate(screenshots):
        print('\tattaching screenshot {}'.format(i+1))
        email.addAttachment(screenshot_path)
      print('End time: \t{}\n'.format(datetime.datetime.now().strftime('%m/%d/%y %I:%M:%S %p')))
      end_time = time.time()
      print_total_elapsed_time(end_time-start_time)
      if send_email == 'YES':
        if mode == 'TEST':
          email.send()
        else:
          if verbose: print("\tDone preparing email... waiting for send time '{}'".format(send_email_time))
          while(True):
            if (current_time>=send_email_time):
              email.send()
              print 'Email sent!'
              break
            time.sleep(10)
      else:   # if send email = 'NO'
        if verbose: print('\tDone preparing email... Opening')
        email.saveAsDraft()
    except Exception as e:
      print('ERROR creating the email')
      print(e)
  else: 
    try:
      email = Outlook(subject=subject, to=to, cc=cc)
      email.addBody(email_body)
      for screenshot_path in screenshots:
        email.addAttachment(screenshot_path)
      print('End time: \t{}\n'.format(datetime.datetime.now().strftime('%m/%d/%y %I:%M:%S %p')))
      end_time = time.time()
      print_total_elapsed_time(end_time-start_time)
      if send_email == 'YES':
        if mode == 'TEST':
          email.send()
        else:
          if verbose: print("\tDone preparing email... waiting for send time '{}'".format(send_email_time))
          while(True):
            if (current_time>=send_email_time):
              email.send()
              print 'Email sent!'
              break
            time.sleep(10)
      else:   # if send email = 'NO'
        if verbose: print('\tDone preparing email... Opening')
        email.saveAsDraft()
    except Exception as e:
      print('ERROR creating the email')
      print(e)
    
  