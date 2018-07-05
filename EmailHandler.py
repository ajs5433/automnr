#!/usr/bin/python

import win32com.client as win32

DEFAULT_EMAIL = 'santosc.aj@hotmail.com'

class Outlook(object):
  def __init__(self, subject="", body = '<br />', recipient=DEFAULT_EMAIL, signature='<br />'):
    self.__outlook      = win32.Dispatch('outlook.application')
    self.__mail         = self.__outlook.CreateItem(0)
    
    self.__attachments  = []
    self.__attach_index = 0

    self.__body         = '<br />'
    self.__signature    = signature
    self.__recipients   = recipient
    self.__mail.Subject = subject
    
  def setSubject(self, subject):
    self.__mail.Subject = subject
    
  def addBody(self, body):
    if not isinstance(body, str):
      return -1
    
    line_break = '<br />'
    self.__body = self.__body + body + line_break
  
  def addAttachment(self, full_path):
    if full_path == None:
      return -1
    
    image_ID = 'ImgID{}'.format(self.__attach_index)
    
    attachment = self.__mail.Attachments.Add(full_path)
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "{}".format(image_ID))
    self.addBody("<html><body> <img src=""cid:{}""></body></html>".format(image_ID))
    
    self.__attach_index = self.__attach_index + 1
    
  def addSignature(self, signature):
    self.__signature = signature
  
  def addRecipient(self, recipient):
    self.__recipients += "; " + recipient
    
  def send(self):
    self.__mail.To        = self.__recipients
    self.__mail.HTMLBody  = self.__body + self.__signature
    
    self.__mail.Send()
    self.__attachments  = []
    self.__attach_index = 0
    
if __name__=='__main__':
  myEmail = Outlook()
  myEmail.addBody('sup my ppls')
  myEmail.addBody('')
  myEmail.addBody('I am the best of them all')
  myEmail.addAttachment("D:\\Users\\BertoTech\\Desktop\\Screenshot_1.png")
  myEmail.addAttachment("D:\\Users\\BertoTech\\Desktop\\Screenshot_2.png")
  myEmail.send()
  