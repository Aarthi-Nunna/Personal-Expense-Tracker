from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from datetime import datetime
from flask_cors import CORS, cross_origin
import ibm_db
import json
import plotly
import plotly.graph_objs as go
import pandas as pd
from flask import send_file
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import base64
from PIL import Image   


app = Flask(__name__, template_folder = 'templates')
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_DEFAULT_SENDER'] = 'nunnaaarthi@gmail.com'
mail = Mail(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# GLobal variables
EMAIL=''
USERID=''

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=nlg66799;PWD=CXtQLAGZ06fD0fhC;","","")

# FUNCTIONS INTERACTING WITH DB # 
def fetch_walletamount():
    sql = 'SELECT WALLET FROM PETA_USER WHERE EMAIL=?'
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, EMAIL)
    ibm_db.execute(stmt)
    user =ibm_db.fetch_assoc(stmt)
    # print(user['WALLET'])
    return user['WALLET'] #returns int
 
def fetch_categories():

    sql = 'SELECT * FROM PETA_CATEGORY WHERE USERID = ?'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,USERID)
    ibm_db.execute(stmt)

    categories = []
    while ibm_db.fetch_row(stmt) != False:
        categories.append([ibm_db.result(stmt, "CATEGORYID"), ibm_db.result(stmt, "CATEGORY_NAME")])

    sql = 'SELECT * FROM PETA_CATEGORY WHERE USERID IS NULL'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)

    while ibm_db.fetch_row(stmt) != False:
        categories.append([ibm_db.result(stmt, "CATEGORYID"), ibm_db.result(stmt, "CATEGORY_NAME")])

    # print(categories)
    return categories # returns list 

def fetch_userID():
    sql = 'SELECT USERID FROM PETA_USER WHERE EMAIL=?'
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, EMAIL)
    ibm_db.execute(stmt)
    user=ibm_db.fetch_assoc(stmt)
    # print(user['USERID'])
    return user['USERID'] # returns int 

def fetch_groups():
    sql = 'SELECT * FROM PETA_GROUPS'
    stmt = ibm_db.exec_immediate(conn, sql)
    groups = []
    while ibm_db.fetch_row(stmt) != False:
        groups.append([ibm_db.result(stmt, "GROUPID"), ibm_db.result(stmt, "GROUPNAME")])
    # print(groups)
    return groups # returns list 

def fetch_expenses() : 
    sql = 'SELECT * FROM PETA_EXPENSE where USERID = ' + str(USERID)
    # print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)
    expenses = []
    while ibm_db.fetch_row(stmt) != False:
        category_id = ibm_db.result(stmt, "CATEGORYID")
        category_id = str(category_id)
        sql2 = "SELECT * FROM PETA_CATEGORY WHERE CATEGORYID = " + category_id
        stmt2 = ibm_db.exec_immediate(conn, sql2)
        category_name = ""
        while ibm_db.fetch_row(stmt2) != False :
            category_name = ibm_db.result(stmt2, "CATEGORY_NAME")
        expenses.append([ibm_db.result(stmt, "EXPENSE_AMOUNT"), ibm_db.result(stmt, "DATE"), ibm_db.result(stmt, "DESCRIPTION"), category_name])
    # print(expenses)
    return expenses

def fetch_limits():
    return range(1000,12001,1000)


# HELPER FUNCTIONS #
def fetch_latest_expenses(expenses):
    # must return expenses of last month
    latest_month = datetime.today().month
    latest_expenses = []
    for exp in expenses:
        if exp[1].month == latest_month:
            latest_expenses.append(exp)

    return latest_expenses

def fetch_monthly_expenses(expenses):
    latest_year = datetime.today().year
    monthly_expenses = {}

    for month in range(1,13):
        monthly_expenses[month]=0

    for exp in expenses:
        if exp[1].year == latest_year:
            monthly_expenses[exp[1].month] += exp[0]


    return monthly_expenses.values()

def draw_graph1(expenses):
    # TOTAL EXPENSE / DAY OF MONTH
    # x-axis: day , y-axis: expense/day
    
    latest_expenses = fetch_latest_expenses(expenses)
    mp = {}
    for day in range(1,31):
        mp[day]=0

    for exp in latest_expenses:
        mp[exp[1].day]+=exp[0]

    x = mp.keys()
    y = mp.values()
    
    # print(mp)

    plt.figure()
    plt.title('Expense recorded over the past month')
    plt.plot(x, y)
    plt.xlabel('Day of the month')
    plt.ylabel('Recorded expense')
    plt.xlim(1,32)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')

    encoded_img_data = base64.b64encode(buffer.getvalue())

    return encoded_img_data

def draw_graph2(expenses, limits):
    # limit/month vs expense/month -> 2 line graphs
    
    monthly_expenses = fetch_monthly_expenses(expenses)
    x = range(1,13)
    y1 = limits
    y2 = monthly_expenses

    plt.figure()
    plt.title('Month-wise comparison of limit and expense')
    plt.plot(x, y1, label = "Limit/month")
    plt.plot(x, y2, label = "Expenses/month")
    plt.xlabel('Month')
    plt.legend()


    buffer = BytesIO()
    plt.savefig(buffer, format='png')

    encoded_img_data = base64.b64encode(buffer.getvalue())

    return encoded_img_data


# END POINTS #
@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    if request.method=='POST':
        email=request.form['email']
        EMAIL=email
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
        EMAIL = email
    return redirect(url_for('dashboard'))

@app.route('/login',methods=['GET','POST'])
def login():
    global EMAIL
    if request.method=='POST':
        email=request.form['email']
        EMAIL=email
        password=request.form['password']
        sql="SELECT * FROM PETA_USER WHERE email=? AND password=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        if account:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    elif request.method=='GET':
        return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    global USERID
    global EMAIL
    if USERID=='' and EMAIL=='':
        return render_template('login.html')
    elif USERID=='':
        USERID=fetch_userID()
    
    expenses = fetch_expenses()
    wallet = fetch_walletamount()
    return render_template('dashboard.html', expenses = expenses, wallet = wallet, email = EMAIL)
      
@app.route('/updatebalance', methods=['GET','POST'])
def update_balance():
    if request.method == 'GET':
        wallet = fetch_walletamount()
        return render_template('updatebalance.html', wallet = wallet)
    elif request.method == 'POST':
        global EMAIL
        global USERID
        if EMAIL == '':
            return render_template('login.html', msg='Login before proceeding')
        if(USERID==''):
            # get user using email
            USERID = fetch_userID()
        
        new_balance = request.form['balanceupdated']
        sql = 'UPDATE PETA_USER SET WALLET = ? WHERE USERID = ?'
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,new_balance)
        ibm_db.bind_param(stmt,2,USERID)
        ibm_db.execute(stmt)

        return redirect(url_for('dashboard'))

@app.route('/addcategory', methods=['GET','POST'])
def add_category():
    if request.method=='GET':        
        # categories = fetch_categories()
        return render_template('addcategory.html')
    
    elif request.method=='POST':
        categoryname  = request.form['category']
        sql = 'INSERT INTO PETA_CATEGORY(CATEGORY_NAME, USERID) VALUES(?,?)'
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,categoryname)
        ibm_db.bind_param(stmt,2,USERID)
        ibm_db.execute(stmt)

        return redirect(url_for('dashboard'))

@app.route('/addgroup', methods=['POST'])
def add_group():
    if request.method == 'POST':
        if USERID == '':
            return render_template('login.html', msg='Login before proceeding')
        sql="INSERT INTO PETA_GROUPS(GROUPNAME, USERID) VALUES(?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,request.form['groupname'])
        ibm_db.bind_param(stmt,2,USERID)
        ibm_db.execute(stmt)
        
        group_info = {}
        
        sql = "SELECT * FROM PETA_GROUPS WHERE GROUPNAME=?"
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, request.form['groupname'])
        ibm_db.execute(stmt)
        group_info = ibm_db.fetch_assoc(stmt)
        return {"groupID": group_info['GROUPID'],'groupname':group_info['GROUPNAME']}

@app.route('/addexpense', methods=['GET', 'POST'])
def add_expense():
    if request.method=='GET':
        groups = fetch_groups()
        categories = fetch_categories()
        if len(categories) == 0:
            return redirect(url_for('add_category'))
        return render_template('addexpense.html', categories=categories, groups=groups)

    elif request.method=='POST':
        global EMAIL
        global USERID
        if EMAIL == '':
            return render_template('login.html', msg='Login before proceeding')
        if(USERID==''):
            # get user using email
            USERID = fetch_userID()
        
        amount_spent = request.form['amountspent']
        category_id = request.form.get('category')
        description = request.form['description']
        date = request.form['date']
        groupid = request.form.get('group')
        # print(amount_spent, category_id, description, date, groupid, USERID)

        sql="INSERT INTO PETA_EXPENSE(USERID, EXPENSE_AMOUNT, CATEGORYID, GROUPID, DESCRIPTION, DATE) VALUES(?,?,?,?,?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,USERID)
        ibm_db.bind_param(stmt,2,amount_spent)
        ibm_db.bind_param(stmt,3,category_id)
        ibm_db.bind_param(stmt,4,groupid)
        ibm_db.bind_param(stmt,5,description)
        ibm_db.bind_param(stmt,6,date)
        ibm_db.execute(stmt)

        sql = "UPDATE PETA_USER SET WALLET = WALLET - ? WHERE USERID = ?";
        statement = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(statement, 1, amount_spent)
        ibm_db.bind_param(statement, 2, USERID)
        ibm_db.execute(statement)
    
        return redirect(url_for('dashboard'))
       
@app.route('/analysis', methods=['GET','POST'])
def analyse():
    if request.method=='GET':
        expenses = fetch_expenses()
        limits = fetch_limits()

        graph1 = draw_graph1(expenses=expenses)
        graph2 = draw_graph2(expenses=expenses,limits=limits)

        return render_template("analysis.html", img_data1=graph1.decode('utf-8'), img_data2=graph2.decode('utf-8'))

    elif request.method=='POST':
        return render_template('analysis.html')

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
    
