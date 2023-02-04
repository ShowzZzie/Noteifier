from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import bcrypt

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

db = SQLAlchemy()

# Configure application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.String, nullable=False)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    reminder_datetime = db.Column(db.String, nullable=False)
    dtobj = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Create the table
with app.app_context():
    db.create_all()


@app.route("/")
def homepage():
    return render_template("home.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['user_id'] = user.id
            print(session['user_id'])
            return redirect('/')
        else:
            flash('Incorrect username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_repeat = request.form['password_repeat']
        user = User.query.filter_by(username=username).first()
        num = False
        upper = False
        for letter in str(password):
            if letter.isnumeric():
                num = True
            if letter.isupper():
                upper = True
        if user:
            flash('Username already exists')
        elif len(str(password)) < 8:
            flash("Password is too short")
        elif num == False:
            flash("Password must contain at least one digit")
        elif upper == False:
            flash("Password must contain an uppercase letter")
        elif password != password_repeat:
            flash("Passwords don't match")
        else:
            hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user = User(username=username, password=hash)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect('/')
    return render_template('register.html')

@app.route('/logout')
def logout():
    # drop session
    try:
        # drop session
        session.pop('user_id')
    except KeyError:
        flash('Logout unsuccessful')
    return redirect('/')

@app.route('/notes')
@login_required
def notes():
    user_id = session['user_id']
    unsorted_notes = Note.query.filter_by(user_id=user_id).all()
    notes = sorted(unsorted_notes, key= lambda x: x.priority, reverse=True)
    return render_template('notes.html', notes=notes)

@app.route("/add_note_f", methods=["GET", "POST"])
@login_required
def add_note():
    title = request.form["title"]
    content = request.form["content"]
    user_id = session['user_id']
    priority = request.form["priority"]
    new_note = Note(title=title, content=content, user_id=user_id, priority=priority)
    db.session.add(new_note)
    db.session.commit()
    return redirect('/notes')

@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def page():
    return render_template("add_note.html")

@app.route("/delete_note", methods=["POST"])
@login_required
def delete_note():
    note_id = request.form["note_id"]
    note = Note.query.get(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect("/notes")


@app.route('/reminders')
@login_required
def reminders():
    user_id = session['user_id']
    unsorted_reminders = Reminder.query.filter_by(user_id=user_id).all()
    reminders = sorted(unsorted_reminders, key=lambda x: x.dtobj)
    now = datetime.now()
    return render_template("reminders.html", reminders=reminders, now=now)

@app.route('/add_reminder_f', methods=["GET", "POST"])
@login_required
def create_reminder():
    title = request.form['title']
    content = request.form.get('content')
    user_id = session['user_id']
    reminder_datetime = datetime.strptime(request.form['reminder_datetime'], '%Y-%m-%dT%H:%M')
    reminder_datetime_formatted = reminder_datetime.strftime("%d/%m/%Y %H:%M")
    new_reminder = Reminder(title=title, user_id=user_id, reminder_datetime=reminder_datetime_formatted, content=content, dtobj=reminder_datetime)
    db.session.add(new_reminder)
    db.session.commit()
    return redirect('/reminders')
    

@app.route('/add_reminder')
@login_required
def create_reminder_page():
    return render_template('add_reminder.html')

@app.route('/delete_reminder', methods=["POST"])
@login_required
def delete_reminder():
    reminder_id = request.form["reminder_id"]
    reminder = Reminder.query.get(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    return redirect("/reminders")


@app.route('/edit_note', methods=["GET", "POST"])
@login_required
def edit_note():
    id = request.form['note_id']
    note = Note.query.get(id)
    return render_template("edit_note.html", note=note)

@app.route('/edit_note_f', methods=["GET", "POST"])
@login_required
def edit_note_f():
    title = request.form['title']
    content = request.form.get('content')
    id = request.form['note_id']
    note = Note.query.get(id)
    note.title = title
    note.content = content
    db.session.commit()
    return redirect('/notes')


@app.route('/edit_reminder', methods=["GET", "POST"])
@login_required
def edit_reminder():
    id = request.form['reminder_id']
    reminder = Reminder.query.get(id)
    return render_template("edit_reminder.html", reminder=reminder)

@app.route('/edit_reminder_f', methods=["GET", "POST"])
@login_required
def edit_reminder_f():
    title = request.form['title']
    content = request.form.get('content')
    id = request.form['reminder_id']
    reminder_datetime = datetime.strptime(request.form['reminder_datetime'], '%Y-%m-%dT%H:%M')
    reminder_datetime_formatted = reminder_datetime.strftime("%d/%m/%Y %H:%M")
    reminder = Reminder.query.get(id)
    reminder.title = title
    reminder.content = content
    reminder.dtobj = reminder_datetime
    reminder.reminder_datetime = reminder_datetime_formatted
    db.session.commit()
    return redirect('/reminders')


if __name__ == '__main__':
    app.run(host='192.168.0.145', port='5000')