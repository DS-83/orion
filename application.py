from flask import Flask, redirect, render_template, request
from flask_login import LoginManager
app = Flask(__name__)

# Create login manager class for flask-login module
login_manager = LoginManager()

# Configure login_manager
login_manager.init_app(app)


@app.route('/')
def login():
    return render_template('login.html')
