import smtplib

def sendemail( to_addr_list,video,concurso,pagina):

    #Definiciones de Configuracion
    from_addr = 'videoconcursos2018@gmail.com'

    subject = 'Tu video  ya ha sido publicado '
    mensaje = 'Tu video  {} ya ha sido publicado en  la pagina publica del concurso {}\n{}'.format(video,concurso,pagina)
    login = 'videoconcursos2018@gmail.com'
    password = 'Uniandes2018'
    smtpserver = 'smtp.gmail.com:587'
    #------------------------------------------
    try:
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(from_addr,to_addr_list[0],subject, mensaje)
        server = smtplib.SMTP(smtpserver)
        server.ehlo()
        server.starttls()
        server.login(login, password)
        problems = server.sendmail(from_addr, to_addr_list, message)
        server.quit()
        return 1
    except:
        return -1


#to_addr_list = ['busongeneral86@hotmail.com']

#sendemail(to_addr_list,'xxx','XXX','XXX.COM')


