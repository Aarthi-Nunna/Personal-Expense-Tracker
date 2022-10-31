import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

app = Flask(__name__, template_folder = 'templates')
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_DEFAULT_SENDER'] = None
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    if request.method == 'POST':
        emailid = request.form['emaill']
        print(emailid)
        msg = Message('Registration Verfication', sender="nunnaaarthi@gmail.com",recipients=[emailid])
        msg.body = ('Congratulations! Welcome user!')
        msg.html = ('<h1>Tegistration Verfication</h1>'
                    '<p>Congratulations! Welcome user! '
                    '<b>PETA</b>!</p>')
        mail.send(msg)
        print("i am working")
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')