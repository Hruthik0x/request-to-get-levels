from email.message import EmailMessage
from ssl import create_default_context 
from smtplib import SMTP_SSL
from json import load
from config import SUBJECT, gen_body
from db import get mail_id_secret_name

with open('confidential.json') as f:
    data = load(f)

SENDER_MAIL = data['SENDER_MAIL']
PASSWORD = data['PASSWORD']

def send_mails() :

    with SMTP_SSL('smtp.gmail.com',465,context=context) as smtp :

        smtp.login(SENDER_MAIL, PASSWORD)
        data = get_mail_id_secret_name()

        for mail_id in data:
            
            email_obj = EmailMessage()
            email_obj['From'] = SENDER_MAIL
            email_obj['To'] = mail_id 
            email_obj['Subject'] = SUBJECT

            body = gen_body(data[mail_id])
            email_obj.set_content(body)
            context = create_default_context()
            smtp.sendmail(SENDER_MAIL, mail_id, email_obj.as_string())
        
if ( __name__ == '__main__' ) :
    send_mails()