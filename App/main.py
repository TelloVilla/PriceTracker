from flask import Flask, render_template, request, url_for, session, redirect
from dotenv import load_dotenv
import pymongo
import os
import bcrypt

load_dotenv()

DB_USER = os.environ.get("DB_USERNAME")
DB_PASS = os.environ.get("DB_PASSWORD")

client = pymongo.MongoClient("mongodb+srv://" + DB_USER + ":" + DB_PASS + DB_SERVER)
db = client.get_database("PriceTracker")
users = db["users"]
records = db.register



app = Flask(__name__)
app.secret_key = "development"

@app.route("/", methods=["post", "get"])
def index():
    message = ""
    if "email" in session:
        return redirect(url_for("hub"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = users.find_one({"email": email})

        if email_found:
            user_email = email_found["email"]
            pass_check = email_found["password"]

            if bcrypt.checkpw(password.encode("utf-8"), pass_check):
                session["email"] = user_email
                return redirect(url_for("hub"))
        else:
            print("Error: Logging in")
            return render_template("landing.html")


    return render_template("landing.html")

@app.route("/hub")
def hub():
    if not "email" in session:
        return redirect(url_for("index"))
    return render_template("hub.html")

@app.route("/items/add", methods=["post", "get"])
def items():
    if not "email" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        item_name = request.form.get("item")
        item_sku = request.form.get("sku")
        item_desc = request.form.get("item-desc")

        item_found = users.find_one({"items.name": item_name})

        if item_found:
            return render_template("items.html")

        new_item = {"name": item_name, "sku": item_sku, "desc": item_desc, "prices": []}


        item_query = {"email": session["email"]}
        item_update = {"$push": {"items": new_item}}

        item_add = users.update_one(item_query, item_update)

        return redirect(url_for("hub"))



    return render_template("items.html")
@app.route("/register", methods=["post", "get"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        user = request.form.get("user")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = users.find_one({"name": user})
        email_found = users.find_one({"email": email})

        if(user_found or email_found):
            print("Record already found")
            return render_template("register.html")
        
        if password1 != password2:
            print("Passwords not equal")
            return render_template("register.html")
        else:
            print("New User Added")
            hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
            user_input = {"name": user, "email": email, "password": hashed, "items": []}
            users.insert_one(user_input)
            return redirect(url_for("hub"))

        


    return render_template("register.html")
