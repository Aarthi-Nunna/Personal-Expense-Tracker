import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

import ibm_db

app = Flask(__name__, template_folder = 'templates')
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_DEFAULT_SENDER'] = 'epicjoe128@gmail.com'
mail = Mail(app)

knt = 0
def increment():
    global knt
    knt += 1

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=nlg66799;PWD=CXtQLAGZ06fD0fhC;","","")

@app.route('/', methods=['GET', 'POST'])
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password'] 
        wallet=request.form['wallet']   
        sql="INSERT INTO PETA_USER(EMAIL,PASSWORD,WALLET) VALUES(?,?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.bind_param(stmt,3,wallet)
        ibm_db.execute(stmt)
        msg = Message('Registration Verfication',recipients=[email])
        msg.body = ('Congratulations! Welcome user!')
        msg.html = ('<h1>Registration Verfication</h1>'
                    '<p>Congratulations! Welcome user!' 
                    '<b>PETA</b>!</p>')
        mail.send(msg)
    return redirect(url_for('dashboard'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        sql="SELECT * FROM PETA_USER WHERE email=? AND password=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    elif request.method=='GET':
        return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')