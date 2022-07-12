import json
import os

import bcrypt
import pymongo
import requests
from flask import Flask, render_template, request, url_for, redirect, session

app = Flask(__name__)
# encryption relies on secret keys so they could be run
# connoct to your Mongo DB database
ConnectionString = "mongodb+srv://admin:admin@documentstm.t4ijg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(ConnectionString)
api_link = "http://127.0.0.1:8000/"
# get the database name
db = client.get_database('User')
# get the particular collection that contains the data
records = db.user_infor
app.secret_key = "CeSTM"
category = os.listdir('D:\\Work\\VBHC_19112021_Result')
from pymongo import MongoClient
from bson.objectid import ObjectId

# import pymongo
_limit_ = 20
global auth
myclient = MongoClient(ConnectionString)
Mydatabase = myclient["DocumentSTM"]
data_source = Mydatabase["STM_DOC"]


def find_by_id(id):
    meta = data_source.find({"_id": ObjectId(id)})
    for i in meta:
        return i


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']

            passwordcheck = email_found['password']
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val

                return redirect(url_for('home'))
            else:
                if "email" in session:
                    return redirect(url_for("home"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)






@app.route('/')
@app.route('/home')
def home():
    if "email" in session:
        # print("ÔKOKOKOKOK")
        data = requests.get(api_link + "all")
        data = data.json()
        # print(data)
        name = records.find_one({'email': session["email"]})["name"]
        return render_template('index.html', name=name, data=data, category=category)
    else:
        return redirect(url_for("login"))


@app.route('/viewPDF')
def viewPDF():
    path = 'D:\\Work\\VBHC_19112021_Result\\Báo cáo'
    a = os.listdir(path)
    # a.remove('.DS_Store')
    text = json.dumps(sorted(a))
    return render_template('viewPDF.html', contents=text)


@app.route("/test", methods=["POST", "GET"])
def test():
    return render_template('test.html')


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
    return redirect(url_for('login'))




@app.route("/signup", methods=['post', 'get'])
def signup():
    message = ''
    # if method post in index
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('signup.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('signup.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('signup.html', message=message)
        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            # insert it in the record collection
            records.insert_one(user_input)

            # find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            # if registered redirect to logged in as the registered user
            return render_template('index.html', email=new_email)
    return render_template('signup.html')


@app.route('/search')
def search():
    question = request.args['search']
    data = requests.get(api_link + "search/?question=" + question).json()

    # data_json = json.loads(data)
    if "email" in session:
        name = records.find_one({'email': session["email"]})["name"]
        for i in data: print(i["doc_type"])

        return render_template('index.html', name=name, data=data, category=category)

    else:
        return redirect(url_for("login"))


@app.route('/category')
def search_category():
    question = request.args['category']
    data = requests.get(api_link + "category/?category=" + question).json()

    # data_json = json.loads(data)
    if "email" in session:
        name = records.find_one({'email': session["email"]})["name"]
        for i in data: print(i["doc_type"])

        return render_template('index.html', name=name, data=data, category=category)
    else:
        return redirect(url_for("login"))


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    return render_template("404.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=True)
