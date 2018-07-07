#!/usr/bin/python

import win32com.client as win32

DEFAULT_EMAIL = 'santosc.aj@hotmail.com'

class Outlook(object):
  def __init__(self, subject="", body = '<br />', To=DEFAULT_EMAIL, cc=DEFAULT_EMAIL , signature='<br />'):
    self.__outlook      = win32.Dispatch('outlook.application')
    self.__mail         = self.__outlook.CreateItem(0)
    
    self.__attachments  = []
    self.__attach_index = 0

    self.__body         = '<br />'
    self.__signature    = signature
    self.__recipients   = To
    self.__carbon_copy  = cc
    self.__mail.Subject = subject
    
  def setSubject(self, subject):
    self.__mail.Subject = subject
    
  def addBody(self, body, replace=True, newline=True):
    """Adds string to html body
    
    body        - string to be added to html body
    replace     - replace option to replace string \n with a <br/> for newline and \t for five spaces
    newline     - adds newline after string automatically. AS print(x) does
    """
    if not isinstance(body, str):
      return -1
    line_break = '<br />'
    if replace:
      body = body.replace('\n',line_break)
      body = body.replace('\t',"    ")
    self.__body = self.__body + body
    if newline:
      self.__body = self.__body + line_break
      
  def addAttachment(self, full_path):
    if full_path == None:
      return -1
    image_ID = 'ImgID{}'.format(self.__attach_index)
    attachment = self.__mail.Attachments.Add(full_path)
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "{}".format(image_ID))
    self.addBody("<html><body> <img src=""cid:{}""></body></html>".format(image_ID))
    self.__attach_index = self.__attach_index + 1
    
  def addSignature(self, signature_path):
    with open(signature_path, 'r', encoding='utf-8') as file:
      for line in file:
        addBody(character, newline=False)
    
  def addRecipient(self, recipient):
    self.__recipients += "; " + recipient
    
  def send(self):
    self.__mail.To        = self.__recipients
    self.__mail.Cc        = self.__carbon_copy
    self.__mail.HTMLBody  = self.__body + self.__signature
    
    self.__mail.Send()
    self.__attachments  = []
    self.__attach_index = 0
    
if __name__=='__main__':
  myEmail = Outlook()
  myEmail.addBody('sup my ppls \n\nI am the best of them all')
  myEmail.addAttachment("D:\\Users\\BertoTech\\Desktop\\Screenshot_1.png")
  myEmail.addAttachment("D:\\Users\\BertoTech\\Desktop\\Screenshot_2.png")
  #myEmail.GetInspector
  myEmail.send()
  