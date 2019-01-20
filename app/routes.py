#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, request, redirect, jsonify
from beebotte import *
from flask_pymongo import PyMongo
from scraping import scrapingfunc
import _thread
import threading
import boto3
from dynamodb_json import json_util as json
import datetime

API_KEY = '8RpTSgXVxjo7yhTobQczfCVu'
SECRET_KEY = 'qVDtlHxpR2Ku6mDLkuQjvV8yMsVoBzDc'

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'scrapDB'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/scrapDB'

mongo = PyMongo(app)

@app.before_first_request
def activate_job():
    thread = threading.Thread(target=scrapingfunc)
    thread.start()



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST" and request.form["Beebotte"] == "Graficas":
        return redirect("https://beebotte.com/dash/dfc1b0b0-ee74-11e8-a140-675e8012aef3#.W_bbTuInbIV", code=302)
    else:
        ahora = datetime.datetime.now()
        ahora_minus_20 = ahora - datetime.timedelta(minutes = 20)
        horadb_minus_20 = ahora_minus_20.strftime("%H:%M:%S")
        fechadb = ahora.strftime("%d/%m/%Y")
        horadb = ahora.strftime("%H:%M:%S")
        dynamodb = boto3.resource('dynamodb', aws_access_key_id='ASIAX4ZBPOMFJ4JQYLJ7',
                                aws_secret_access_key='jf8iWBVxdABnHGNNJ9fztjt//hOFOiDHFLqy959/',
                                region_name='us-east-1',
                                aws_session_token='FQoGZXIvYXdzEEAaDCfgS7i/IaOp2WkmlSLoAhifl4vayvoHoPb6ImS9R06JBeGvikMLaLhh4uDa17kNnvD0OSt0wPrpD0O60RxPkXrVBR3VuI4VkIC0qcXF58UQawTxJ2JCCN3RPwI4LvJxqXedYYF3Zrlb9jmsRk+aAPc4oaGEtDwQhv87vnEE6ANcFuSGiBpKqtiP7mV8ffg8rOgx8E6dankyJ42R7l4LpjPtsb0TpkD+VWgAr/0RwnIENC1Nd/OoE1tQBlHbQWE82SSW74BqfpVuGKbj3csemVqwYWi6sbAcaxCVEMwsv5cB6m/poAA4aXC/QKBxyKzr8O61IoZx5oXTs5llaYzz/m/dLc8QLOVZ1EVaaTYGHNoeC40FiKx/+2+zMe8wEHT1lsP1F3I4F+zUQrkQMf0T8RX3Sd5y9u9SyhQFo0i0PKQNcvE1ibIeJ1DOqSFGJH47Ll4mPM/gckbUEHCh422n2KTKAIzmv035NjY1pi0nulyLSqgs0hTRnCjhjZLiBQ=='
                  )
        table = dynamodb.Table('scrapingTabla')
        response = table.scan(FilterExpression= "Fecha = :fechadb and Hora between :lo and :hi", ExpressionAttributeValues= {":fechadb": fechadb, ":lo": horadb_minus_20, ":hi": horadb})
        scrap_list = mongo.db.scrapings.find().sort('_id', -1).limit(10);
        return render_template('home.html', scrap_list = json.loads(response['Items']))

@app.route("/umbral", methods=["GET", "POST"])
def formumbral():
    count = 0
    umbral = 0 
    if request.method == "POST":
        superiores = []
        umbral = int(request.form["umbral"])
        scrap_list = mongo.db.scrapings.find({ "meneo": { "$gt": umbral } }).sort('_id', -1).limit(10);
        count = scrap_list.count();
        if count > 10:
            count = 10
        return render_template('formumbral.html', scrap_list = scrap_list, cuenta = count)
    else:    
        return render_template('formumbral.html', cuenta = count)

    
@app.route("/media/<database>")
def background_process(database):
    if database == "local":
        promedio_local = 0
        #media = mongo.db.scrapings.aggregate([{ "$group": {"_id":null, "average": {"$avg": "$clic"} }}]);
        media = mongo.db.scrapings.find().sort('_id', -1).limit(500);
        for dato in media:
            promedio_local =  promedio_local + int(dato['clic'])       
        promedio_local = float(promedio_local/500)
        return jsonify({'result': promedio_local, 'resultbd': "Local"})      
    elif database == "remota":
        promedio_remoto = 0
        bclient = BBT(API_KEY, SECRET_KEY)
        bclient = BBT(token = "token_mIi9pRj5MYYw1GwA")
        databebo = bclient.read('ScrapingMeneate', 'Clics', limit = 500)
        total = len(databebo)
        for dato in range(total):
            promedio_remoto =  promedio_remoto + int(databebo[dato]['data'])       
        promedio_remoto = promedio_remoto/total
        return jsonify({'result': promedio_remoto, 'resultbd': "Remota"})      
    else:
        return jsonify({'result': 0, 'resultbd': "Ninguna"})
    
@app.route("/interactiva")
def interactiva():
    return render_template("formmedia.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__ == "__main__":
    #scrapingfunc()
    #_thread.start_new_thread(scrapingfunc, ())
    start_runner()
    app.run(debug=True)

