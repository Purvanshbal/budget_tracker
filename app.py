from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
#The first page that opens is the login page for the budget tracker. So an empty request renders index.html (which has the login stuff)
def hello():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')    

if __name__ == '__main__':
    app.run(debug=True)