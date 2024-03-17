from flask import Flask, render_template, url_for, request, redirect, session, flash, get_flashed_messages

# Database 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

# Password hashing
import bcrypt

# Password strength Verification
from zxcvbn import zxcvbn

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'SECRET_KEY'


# class name is table name
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(30), default='default')

    # notes = db.relationship('UserData', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f"{self.username} is Registered"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    organizer_name = db.Column(db.String(80), nullable=True)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('events', lazy=True))

    def __repr__(self) -> str:
        return f"{self.title} is Organized by {self.organizer.username}"


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('registrations', lazy=True))
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))


# initialize the database
with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['username'] = user.username
            session['role'] = user.role
            # return redirect('/dashboard')
            return redirect('/event')
        if not user:
            return render_template('signin.html', msg="User does not exists.")
        if user and user.password != password:
            return render_template('signin.html', msg="Incorrect Password")

    return render_template('signin.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        iusername = request.form.get("username")
        ipassword = request.form.get("password")
        icpassword = request.form.get("cpassword")
        user = User.query.filter_by(username=iusername).first()
        if user:
            return render_template('signup.html', msg="User already exists")
        if zxcvbn(ipassword)["score"] < 2:
            return render_template('signup.html', msg=f"{zxcvbn(ipassword)['feedback']['warning']}")
        if ipassword == icpassword:
            # Generating hashed Password
            # salt = bcrypt.gensalt()
            hashPassword = bcrypt.hashpw(ipassword.encode('utf-8'), bcrypt.gensalt())

            user = User(username=iusername,
                        password=hashPassword)
            db.session.add(user)
            db.session.commit()
            # alldata = Table.query.all()
            # print(alldata)
            print(user)
            return redirect(url_for('signin'))
        else:
            return render_template('signup.html', msg="Password does not match.")
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('role')
    return redirect('/signin')


@app.route('/database', methods=["GET"])
def data():
    alldata = User.query.all()
    # print(alldata)
    return render_template('database.html', alldatas=alldata)


@app.route('/event', methods=["GET", "POST"])
def event():
    # events = Event.query.filter(Event.date >= datetime.utcnow()).all()
    events = Event.query.all()
    msg = get_flashed_messages()
    return render_template('event.html', msg=msg, events=events)


@app.route('/event/register', methods=["GET", "POST"])
def register():
    if 'username' in session:
        if request.method == "POST":
            event_id = request.form.get('event_id')
            user_id = session['username']
            if Registration.query.filter_by(user_id=user_id, event_id=event_id).first():
                flash("You have already registered for this event")
                return redirect(url_for('event'))
            registration = Registration(user_id=user_id, event_id=event_id)
            db.session.add(registration)
            db.session.commit()
            flash("You have successfully registered for the event")
            return redirect(url_for('event'))
    return redirect(url_for('signin'))


@app.route('/event/create', methods=['GET', 'POST'])
def create_event():
    if 'username' in session:
        if session['role'] == 'Admin' or session['role'] == 'Co-Admin':
            if request.method == 'POST':
                title = request.form.get('title')
                description = request.form.get('description')
                date = request.form.get('date')
                date = datetime.strptime(date, '%Y-%m-%d').date()
                location = request.form.get('location')
                creator_id = session['username']
                organizer_name = request.form.get("organizer_name")

                event = Event(title=title, description=description, date=date, location=location, creator_id=creator_id)
                db.session.add(event)
                db.session.commit()

                flash('Event created successfully')
                return redirect(url_for('event'))

            return render_template('create_event.html')
        else:
            flash('You are not authorized to access this page')
            return redirect(url_for('event'))

    return redirect(url_for('signin'))


@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if 'username' in session:
        if User.query.filter_by(username=session['username']).first().role == 'Admin':
            # The following code is for pagination to display 10 users per page
            page = request.args.get('page', 1, type=int)
            # users = User.query.all()
            users = User.query.paginate(page=page, per_page=10, error_out=False)

            if request.method == 'POST':
                search = request.form.get('search')
                if search:
                    search_result = User.query.filter(User.username.like('%' + search + '%')).all()
                    return render_template('user_management.html', users=search_result)

            msg = get_flashed_messages()
            return render_template('user_management.html', users=users, msg=msg)
        else:
            flash('You are not authorized to access this page')
            return redirect(url_for('event'))

    return redirect(url_for('signin'))


@app.route('/event_manager', methods=['GET', 'POST'])
def event_manager():
    page = request.args.get('page', 1, type=int)
    reg = Registration.query.paginate(page=page, per_page=10, error_out=False)
    total_result = Registration.query.count()
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            # search_result = Registration.query.filter(Registration.event.title.like('%' + search + '%')).all()
            search_result= Registration.query.filter(Registration.event.has(title='%'+search+'%')).all()
            total_result = Registration.query.filter(Registration.event.has(title='%'+search+'%')).count()
            return render_template('event_manager.html', events=search_result, total_result=total_result)
        else:
            flash('No results found')

    msg = get_flashed_messages()
    return render_template('event_manager.html', events=reg, msg=msg, total_result=total_result)


@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user.username == session['username']:
        flash('You cannot delete yourself')
        return redirect(url_for('user_management'))

    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
    else:
        flash('User not found')
    return redirect(url_for('user_management'))


@app.route('/change_role', methods=['POST'])
def change_role():
    username = request.form.get('username')
    new_role = request.form.get('role')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return {"error": "User not found"}, 404

    user.role = new_role
    db.session.commit()

    flash('Role changed successfully')
    return redirect(url_for('user_management'))


# Just for testing
@app.route('/admin', methods=["GET"])
def create_admin_account():
    admin_username = 'admin'
    admin_password = '1Parul2University3'
    admin_role = 'Admin'
    hashPassword = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

    admin = User.query.filter_by(username=admin_username).first()
    if admin is None:
        admin = User(username=admin_username, password=hashPassword, role=admin_role)
        db.session.add(admin)
        db.session.commit()
    return redirect('signin')


if __name__ == '__main__':
    app.run(debug=True)
