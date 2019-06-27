import os
import sendgrid
from sendgrid.helpers.mail import *


def sendemail( to_addr_list,video,concurso,pagina):
    try:
        if to_addr_list[0]:
            mensaje = 'Tu video  {} ya ha sido publicado en  la pagina publica del concurso {}\n{}'.format(video,concurso,pagina)
            sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email("videoconcursos2018@gmail.com")
            to_email = Email(to_addr_list[0])
            subject = "Tu video  ya ha sido publicado "
            content = Content("text/plain", mensaje)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            #print(response.status_code)
            #print(response.body)
            #print(response.headers)

        else:
            print('no hay direccion de destiantario')
        return 1
    except:
        print('error en el envio del correo')
        return -1

