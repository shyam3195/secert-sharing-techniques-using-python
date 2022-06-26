import logging
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from utils.secrets import sender_email_address, sender_email_password
def send_email(receiver_address, message, subject):
    try: 
        #Create your SMTP session 
        smtp = smtplib.SMTP('smtp.outlook.com', 587) 

        #Use TLS to add security 
        smtp.starttls() 

        #User Authentication 
        smtp.login(sender_email_address, sender_email_password)
  
        msg = MIMEMultipart()       # create a message


        # setup the parameters of the message
        msg['From']=sender_email_address
        msg['To']=receiver_address
        msg['Subject']="This is Secret Message For "+subject
        
        # add in the message body
        msg.attach(MIMEText(str(message), 'plain'))
        
        # send the message via the server set up earlier.
        smtp.send_message(msg)
        del msg 

        logging.info ("Email sent successfully!") 

    except Exception as ex: 
        logging.warning("Something went wrong....")
        logging.error(ex)
