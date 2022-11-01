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
app.config['MAIL_DEFAULT_SENDER'] = 'josephimmanuel19044@cse.ssn.edu.in'
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    if request.method == 'POST':
        emailid = request.form['emaill']
        print(emailid)
        msg = Message('Registration Verfication',recipients=[emailid])
        msg.body = ('Congratulations! Welcome user!')
        msg.html = ('<h1>Registration Verfication</h1>'
                    '<p>Congratulations! Welcome user!' 
                    '</br><b>PETA</b>!</p>')
        mail.send(msg)
        print("i am working")
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')