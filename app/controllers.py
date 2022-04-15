from flask import render_template, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import current_app as app
from .models import User, Tracker, Data
from .database import db

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    name = StringField('name', validators=[InputRequired(), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/') #homepage
def home():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(username=form.username.data).first()
        if usr:
            if check_password_hash(usr.password, form.password.data):
                login_user(usr, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return '<h1>Invalid username or password.</h1>'
    return render_template('/login_page/login.html', form=form)

@app.route("/dashboard", methods = ['GET', "POST"])
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'GET':
        trackers = Tracker.query.filter_by(user_id = current_user.id).all()
        logs = Data.query.order_by(Data.timestamp.desc()).all()
        #logs = Data.query.filter_by(tracker_id = trackers[0])
        return render_template("dashboard.html", name = current_user.name, trackers = trackers, logs = logs)

@app.route('/register',  methods = ['GET', 'POST'])
def register_new():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, name = form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('/login_page/register.html', form=form)


# tracker routes

@app.route("/log/<int:tracker_id>", methods = ['GET', 'POST'])
def tracker(tracker_id):
    tracker_details = Tracker.query.filter_by(id=tracker_id).first()
    if request.method == 'GET':
        return render_template('log_tracker.html', tr_details = tracker_details)
    if request.method == 'POST':
        value = request.form['value']
        note = request.form['note']
        new_log = Data(user_id = current_user.id, tracker_id = tracker_id, value=value, note=note)
        db.session.add(new_log)
        db.session.commit()
        return redirect('/dashboard')

@app.route('/tracker/add', methods = ['GET', 'POST'])
def add_tracker():
    if request.method == 'GET':
        return render_template('add_tracker.html')
    else:
        name = request.form['name']
        type = request.form['type']
        mcb = request.form['mcqa']
        if request.form['type'] == 'Mul':
            new_tracker = Tracker(name=name, type=type, mcb=mcb, user_id = current_user.id)
        elif request.form['type'] == 'Bool':
            mcb = 'True,False'
            new_tracker = Tracker(name=name, type=type, mcb=mcb, user_id = current_user.id)
        else:
            new_tracker = Tracker(name=name, type=type, user_id = current_user.id)
        db.session.add(new_tracker)
        db.session.commit()
        return redirect(url_for('dashboard'))

@app.route("/delete/<int:tracker_id>", methods = ['GET', 'POST'])
def delete_tracker(tracker_id):
    if request.method == 'GET':
        temp = Tracker.query.filter_by(id=tracker_id, user_id = current_user.id).first()
        db.session.delete(temp)
        temp = Data.query.filter_by(tracker_id=tracker_id, user_id = current_user.id).all()
        for tem in temp:
            db.session.delete(tem)
        db.session.commit()
        
        return redirect('/dashboard')

@app.route("/tracker/logs/<int:tracker_id>", methods = ['GET', 'POST'])
def tracker_logs(tracker_id):
    if request.method == 'GET':
        logs = Data.query.filter_by(tracker_id=tracker_id, user_id = current_user.id).order_by(Data.timestamp.desc())
        return render_template('tracker_logs.html', logs=logs)
    
@app.route('/delete/log/<tracker_id>/<timestamp>')
def delete_log(tracker_id, timestamp):
    if request.method == 'GET':
        log = Data.query.filter_by(user_id=current_user.id, tracker_id=tracker_id, timestamp=timestamp).first()
        db.session.delete(log)
        db.session.commit()
        return redirect('/tracker/logs/'+tracker_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
