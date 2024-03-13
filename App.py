from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'SECRET_KEY'

# class name is table name
class Table(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.username} is Registered"


# initialize the database
with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Table.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['username'] = user.username
            # session["password"] = user.password
            return redirect('/dashboard')
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
        user = Table.query.filter_by(username = iusername).first()
        if user:
            return render_template('signup.html', msg="User already exists")
        if len(ipassword) < 5:
            return render_template('signup.html', msg="Password is too short")
        if ipassword == icpassword:
            # Generating hashed Password
            # salt = bcrypt.gensalt()
            hashPassword = bcrypt.hashpw(ipassword.encode('utf-8'), bcrypt.gensalt())

            user = Table(username=iusername,
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


@app.route('/dashboard', methods=["GET"])
def dashboard():
    if session["username"]:
        return f"Welcome {session["username"]}!"
    redirect('/signin')


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/signin')


@app.route("/database", methods=["GET"])
def data():
    alldata = Table.query.all()
    # print(alldata)
    return render_template('database.html', alldatas=alldata)


if __name__ == '__main__':
    app.run(debug=True)
