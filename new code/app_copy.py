# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 10:25:07 2022

@author: 91900
"""
from flask import Flask, render_template, url_for,session,request, redirect
import ibm_db

app=Flask(__name__, template_folder='/pages')
app.secret_key='a'
conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wym47343;PWD=KRCuyIBtvZY1adNZ;","","")
@app.route('/', methods=['GET','POST'])
def register():
    msg=" "
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']    
        # sql="INSERT INTO user_aarthin VALUES(?,?,?,?)"
        # stmt=ibm_db.prepare(conn,sql)
        # ibm_db.bind_param(stmt,1,email)
        # ibm_db.bind_param(stmt,2,password)
        # ibm_db.bind_param(stmt,3,rollno)
        # ibm_db.bind_param(stmt,4,password)
        # ibm_db.execute(stmt);
        msg='Succesfully registered!'
        return render_template('check.html')
        # return redirect(url_for('login'))
    elif request.method=='GET':
        msg='Please fill the form'
    return render_template('register.html',msg=msg)


@app.route("/login",methods=['GET','POST'])
def login():
    global userid
    msg=" "
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        sql="SELECT * FROM user WHERE username=? AND password=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin']=True
            session['id']=account['USERNAME']
            userid=account['USERNAME']
            session['username']=account["USERNAME"]
            msg='Logged in successfully'
            return render_template("welcome.html",msg=msg,username=userid)
        else:
            msg='Incorrect username/password'
            return render_template('login.html', msg=msg)
    elif request.method=='GET':
        return render_template('login.html')
        
        
if __name__=='__main__':
    app.run(host='0.0.0.0')
