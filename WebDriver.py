#!/usr/bin/python

from selenium import webdriver                                    # basic driver
from selenium.webdriver.common.by import By                       # To make website wait
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

class WebDriver():
  def __init__(self, login_url, username="", password="", username_id="login_email", password_id="login_password", login_required=True):
    """
    Initializes the web browser variables
    username    - username to be intered
    password    - password to the given username
    username_id - identifier of the name field on the website where username will be entered.
    password_id - identifier of the password field. Both ids are obtained by Inspecting the elemennt
    """

    self.__browser = webdriver.Firefox()
    self.__browser.execute_script("document.body.style.zoom='{} %'".format(zoom))
    self.__browser.get(login_url)
    if login_required:
      login_email     = self.__browser.find_element_by_id(username_id).send_keys(username)
      login_password  = self.__browser.find_element_by_id(password_id).send_keys(password)
      self.__browser.find_element_by_name('commit').click()
    
  
  def printWebsite(self, link="https://www.google.com.do/", file_save_path="out.png"):
    self.__browser.get_screenshot_as_file(file_save_path)

  def close(self):
    self.__browser.quit()
    
if __name__=='__main__':
  link = 'data:image/jpeg;base64,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'
  firefox = WebDriver("https://www.google.com.do/",login_required=False)
  firefox.printWebsite(file_save_path="out{}.png".format(0))
  firefox.close()
  #driver.execute_script("document.body.style.zoom='zoom %'")