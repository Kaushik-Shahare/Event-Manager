from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# class name is table name
class Table(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.username}"


# initialize the database
with app.app_context():
    db.create_all()

# class Users(UserMixin, db.Model):
#     id = db.column(db.Integer, primary_key=True)
#     username =


@app.route('/', methods=["GET", "POST"])
@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Table.query.filter_by(username=username).first()
        if user and user.password == password:
            return "Login Successfull"

    return render_template('signin.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        iusername = request.form.get("username")
        ipassword = request.form.get("password")
        icpassword = request.form.get("cpassword")
        if ipassword == icpassword:
            user = Table(username=iusername,
                         password=ipassword)
            # col = Table(title="Title of the Note 1000000", desc="Description of the Note")
            db.session.add(user)
            db.session.commit()
            alldata = Table.query.all()
            print(alldata)
    return render_template('signup.html')


@app.route("/database", methods=["GET"])
def data():
    alldata = Table.query.all()
    print(alldata)
    return render_template('index.html', alldatas=alldata)


if __name__ == '__main__':
    app.run(debug=True)
