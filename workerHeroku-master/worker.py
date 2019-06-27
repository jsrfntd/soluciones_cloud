#!/usr/bin/env python3
# ---IMPORTACION DE LIBREIRAS----------------------
def workerh():
    import time
    import datetime
    start = time.time()
    print('worjer inicia a las: ', str(datetime.datetime.now()))
    import os
    import subprocess as sp
    from emailsender import sendemail
    #import psycopg2
    #from pandas import DataFrame
    import re
    #import random

    import boto3
    #import botocore

    import pymongo
    #from pprint import pprint

    import ffmpy

    # ------INICIALIZACION DE VARIABLES-----------------------
    workerNo = '1'

    # -- CONEXION CON COLA SQS---------------------

    region_name = 'us-east-1'
    queue_name = 'videoQ'

    aws_access_key_id = os.environ['AWSID']
    aws_secret_access_key = os.environ['AWSK']

    sqs = boto3.resource('sqs', region_name=region_name,
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key)

    queue = sqs.get_queue_by_name(QueueName=queue_name)

    # -------CONEXION A S3--------------------------------------
    s3 = boto3.resource('s3', region_name=region_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)
    BUCKET_NAME = 'vcm.uniandes.grupo4'


    # -------FUNCIONES--------------------------------------
    def convertVideo(inputV, outputV):
        cmd = 'ffmpeg -n -loglevel error -hide_banner -i %s -vcodec h264  -c:a aac  -strict -2 -preset veryfast %s' % (
            inputV, outputV)
        # try:
        sp.call(cmd, shell=True)
        return 1
        # except:
        # return -1


    # --------CONEXION A MONGO-----------------------
    client = pymongo.MongoClient(str(os.environ['MONGO']))
    db = client.hola

    #--------BORRAR TEMPORALES----------------------------------

    def delTemp():
        cmd = 'rm ./tmp/originales/*.*'
        cmd2 = 'rm ./tmp/convertidos/*.*'
        try:
            sp.call(cmd, shell=True)
            sp.call(cmd2, shell=True)
            return 1
        except:
            return -1


    # --------DESCARGAR VIDEOS DE S3 PARA VONVERTIRLOS----------------


    # LEER MENSAJES
    max_queue_messages = 1
    message_bodies = []
    messages_to_delete = []

    response = queue.receive_messages(MaxNumberOfMessages=max_queue_messages)
    # pprint(response)
    conta = 0
    for message in response:
        URL = message.body
        m = re.search('.+/media/videosOriginales/(.+)', URL)
        # print(m)
        if m:

            fname = m.group(1)
            name = fname.split('.')
            # print(name)
            if len(name) > 1:
                fnameC = name[0] + '.mp4'
                TEMPI = './tmp/originales/%s' % fname
                #print(TEMPI)
                TEMPO = './tmp/convertidos/%s' % fnameC
                #print(TEMPO)
                KEY = 'media/videosOriginales/%s' % fname
                s3.Bucket(BUCKET_NAME).download_file(KEY, TEMPI)
                # print(TEMPI, TEMPO)
                x = convertVideo(TEMPI, TEMPO)
                # print(x)
                if x == 1:
                    # print('Buena')
                    # -----------SUBIR VIDEO CONVERTIDO-----------------------------------------------------------------
                    procesado = 'videosProcesados/' + fnameC  # + workerNo + 'W' + str(random.randint(0, 9))
                    s3.Bucket(BUCKET_NAME).upload_file(TEMPO, 'media/' + procesado, ExtraArgs={'ACL': 'public-read'})
                    messages_to_delete.append({'Id': message.message_id, 'ReceiptHandle': message.receipt_handle})
                    delete_response = queue.delete_messages(Entries=messages_to_delete)
                    messages_to_delete = []

                    # --------------CONSULTAR Y UPDATE MONGO ------------------------------------------------------------

                    fupdate = db.vcm_video_participante.find_one_and_update(
                        {'estado': 1, 'video_original': 'videosOriginales/' + fname},
                        {'$set': {'estado': 2, 'video_porcesado': procesado}})
                    # pprint(fupdate)
                    # print(fname)
                    # print(procesado)
                    conta = conta + 1
                    to_addr_list = [fupdate['correo_participante']]
                    video = fupdate['descripcion']
                    consulta = db.vcm_concurso.find_one({'id': fupdate['concurso_id']})
                    concurso = consulta['nombre']
                    pagina = 'https://appvideoscontest.herokuapp.com' + '/participar/' + consulta['url']
                    sendemail(to_addr_list, video, concurso, pagina)

    end = time.time()
    doc = {"date": datetime.datetime.now(), "videosConvertidos": conta, "tiempoConversion": end - start}

    db.vcm_estres.insert_one(doc)

    client.close()


    print('tarea terminada tomo: ', end - start, ' videos convertios: ', conta)


