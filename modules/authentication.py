from modules import app
from .models import db, User
from flask import render_template, url_for, request, redirect, session

# Password hashing
import bcrypt

# Password strength Verification
from zxcvbn import zxcvbn


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
            session['theme'] = ''
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
    session.pop('theme')
    return redirect('/signin')

    
@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    current_theme = session['theme']
    new_theme = '' if current_theme == 'light-theme' else 'light-theme'
    session['theme'] = new_theme
    return redirect(request.referrer)

    
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
