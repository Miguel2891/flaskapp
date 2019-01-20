#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import schedule
import boto3
import datetime
import time
from beebotte import *
from pymongo import MongoClient

API_KEY = '8RpTSgXVxjo7yhTobQczfCVu'
SECRET_KEY = 'qVDtlHxpR2Ku6mDLkuQjvV8yMsVoBzDc'

def scrapingfunc():
    while True:
        time.sleep(120 - (time.time() % 120))
        ahora = datetime.datetime.now()
        fechadb = ahora.strftime("%d/%m/%Y")
        horadb = ahora.strftime("%H:%M:%S")
        htmlpage = urlopen('https://www.meneame.net').read()
        soup = BeautifulSoup(htmlpage, "html.parser")
    # get title
        titulo = soup.find('div', attrs={'class': 'center-content'}).h2.contents[1].text
        title_pattern = re.compile(r'^\s*(.*)\s$')
        title= title_pattern.findall(titulo)
        titledb = title[0]
    # get meneos
        meneo = soup.find('div', attrs={'class': 'news-body'}).find('a').text
        meneo_pattern = re.compile(r'^\s*(.*)\s*$')
        meneo_number= meneo_pattern.findall(meneo)
        meneodb = int(meneo_number[0])
    #get clics
        clic =soup.find('div', attrs={'class': 'news-body'}).find('div', attrs={'class': 'clics'}).text
        clic_pattern = re.compile(r'(\w+)')
        clic_number= clic_pattern.findall(clic)
        clicdb = int(clic_number[0])

    #insertamos en la base de datos local
        client = MongoClient('localhost:27017')
        db = client.scrapDB
        myrecord = {
            "fecha": fechadb,
            "hora" : horadb,
            "titulo" : titledb,
            "meneo" : meneodb,
            "clic" : clicdb
        }
        db.scrapings.insert(myrecord)
        

    #insertamos en la base de datos Cloud Beebotte
        bclient = BBT(API_KEY, SECRET_KEY)
        bclient = BBT(token = "token_mIi9pRj5MYYw1GwA")

        bclient.write('ScrapingMeneate', 'Fecha', fechadb)
        bclient.write('ScrapingMeneate', 'Hora', horadb)
        bclient.write('ScrapingMeneate', 'Titulo', titledb)
        bclient.write('ScrapingMeneate', 'Meneos', meneodb)
        bclient.write('ScrapingMeneate', 'Clics', clicdb)

    #insertamos en la base de datos AWS DYNAMODB
        
        dynamodb = boto3.client('dynamodb', aws_access_key_id='ASIAX4ZBPOMFJ4JQYLJ7',
                                   aws_secret_access_key='jf8iWBVxdABnHGNNJ9fztjt//hOFOiDHFLqy959/',
                                   region_name='us-east-1',
                                    aws_session_token='FQoGZXIvYXdzEEAaDCfgS7i/IaOp2WkmlSLoAhifl4vayvoHoPb6ImS9R06JBeGvikMLaLhh4uDa17kNnvD0OSt0wPrpD0O60RxPkXrVBR3VuI4VkIC0qcXF58UQawTxJ2JCCN3RPwI4LvJxqXedYYF3Zrlb9jmsRk+aAPc4oaGEtDwQhv87vnEE6ANcFuSGiBpKqtiP7mV8ffg8rOgx8E6dankyJ42R7l4LpjPtsb0TpkD+VWgAr/0RwnIENC1Nd/OoE1tQBlHbQWE82SSW74BqfpVuGKbj3csemVqwYWi6sbAcaxCVEMwsv5cB6m/poAA4aXC/QKBxyKzr8O61IoZx5oXTs5llaYzz/m/dLc8QLOVZ1EVaaTYGHNoeC40FiKx/+2+zMe8wEHT1lsP1F3I4F+zUQrkQMf0T8RX3Sd5y9u9SyhQFo0i0PKQNcvE1ibIeJ1DOqSFGJH47Ll4mPM/gckbUEHCh422n2KTKAIzmv035NjY1pi0nulyLSqgs0hTRnCjhjZLiBQ=='
                   )
        dynamodb.put_item(
            TableName='scrapingTabla', 
            Item={
                    'Titulo': {'S': titledb},
                    'Hora': {'S': horadb},
                    'Fecha': {'S': fechadb},
                    'Meneo': {'N': str(meneodb)},
                    'Clic': {'N': str(clicdb)}
                }
         )
        #schedule.every(2).minutes.do(scrapingfunc)
        #while True:
        #  schedule.run_pending()
        #  time.sleep(1)
         
        #esperamos 2 minutos
        #time.sleep(120 - (time.time() % 120))

                   


    

