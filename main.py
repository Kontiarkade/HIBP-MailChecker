#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from flask import send_from_directory

import secrets
import csv
import time

from MailChecker import MailChecker


app = Flask(__name__)
app.secret_key = secrets.token_hex()

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def errorpage(error):
    s ='/\\'
    randomString =''
    #possible dirbuster protection part
    for i in range(60):
        randomString += secrets.choice(s)
    if error==400 or error==401:
        return render_template(
            'generic-error.html',
            error=error + error.description,
            randomString=randomString
            )
    return render_template('generic-error.html',
                            error=error,
                            randomString=randomString)    


@app.route('/stringcheck', methods=['GET', 'POST'])
def stringcheck():
    return render_template('stringcheck.html')

@app.route('/filecheck')
def apichek():
    return render_template('filecheck.html')

@app.route('/status', methods=['POST', 'GET'])
def status():
    if request.method == 'POST':
        a = request.form['apikey']
        if 'stream' in request.files:
            s = str(request.files['stream'].read())
        else:
            s = request.form['stream']
        job = MailChecker(key=a, stream=s)
    else:
        abort(500)        
    try:
        res = job.checkAll()
        reportName = 'Checker_report_' + time.strftime("%d%m%Y-%H%M") + '.csv'
        with open('storage/'+reportName, 'w', newline='') as csvfile:
            fieldnames = [key for key in res[1].keys()]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for values in res.values():
                writer.writerow(values)
    except ValueError as e:
        abort(400, str(e))
    except AssertionError as e:
        abort(401, str(e))
    return render_template(
        'status.html',
        emails=job.l,
        result=res,
        reportName=reportName
        )

@app.route('/storage/<path:filename>')
def download_file(filename):
    return send_from_directory(directory='storage', path=filename)

if __name__ == '__main__':
    app.run(debug=True)