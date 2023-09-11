from flask import Flask
from flask import render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)

#secret key
app.config['SECRET_KEY'] = "my super secret key"

#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#Initialize the db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Submit")

#Create a Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password_hash = db.Column(db.String(250))
    

    @property
    def password(self):
        raise AttributeError("Password is not readable!!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name

#Create a Form class
class UserForm(FlaskForm):
    name = StringField("Name", validators = [DataRequired()])
    email = StringField("Email", validators = [DataRequired()])
    password_hash = PasswordField("Password", validators = [DataRequired(), EqualTo("password_hash2", message = "Passwords Must Match!")])
    password_hash2 =  PasswordField("Confirm Password", validators = [DataRequired()])
    submit = SubmitField("Submit")
    

@app.route('/', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.username.data).first()
        if user:
            #check the has
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfull!") 
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password!")
        else:
            flash("Incorrect Username!")     
    return render_template('login.html', form = form)

#Create Logout Page
@app.route('/logout/', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))

#Create Dashboard Page
@app.route('/dashboard/', methods = ['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/user/add', methods = ["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name = form.name.data, email = form.email.data, password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data 
        form.name.data = ""
        form.email.data = ""
        form.password_hash = ""
        flash("USER ADDED SUCCESFULLY")   
    our_users = Users.query
    return render_template('add_user.html', form = form, name = name, our_users = our_users)

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        our_users = Users.query
        return render_template('add_user.html', form = form, name = name, our_users = our_users)
    except:
        flash("OHNOO!!")
        return render_template('add_user.html', form = form, name = name, our_users = our_users)

if __name__ == '__main__':
    app.run(debug=True)