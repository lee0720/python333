from flaskr import app
from flask import render_template,request,redirect,url_for
import sqlite3
DATABASE = 'database.db'

@app.route('/')
def index():
    return render_template(
        'index.html'
    )

@app.route('/form')
def form():
    return render_template(
        'form.html'
    )

@app.route('/register',methods=['POST'])
def register():
    title = request.form['title']
    price = request.form['price']
    arrival_day = request.form['arrival_day']

    con = sqlite3.connect(DATABASE)
    con.execute('INSERT INTO books VALUES(?,?,?)',
                [title,price,arrival_day])
    con.commit()
    con.close()
    return redirect(url_for('index'))