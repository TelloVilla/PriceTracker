from flask import Flask, render_template, request, url_for, session, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import pymongo
import os
import bcrypt
import random
import json
import pandas as pd

load_dotenv()

DB_USER = os.environ.get("DB_USERNAME")
DB_PASS = os.environ.get("DB_PASSWORD")
DB_SERVER = os.environ.get("DB_SERVER")

client = pymongo.MongoClient("mongodb+srv://" + DB_USER + ":" + DB_PASS + DB_SERVER)
db = client.get_database("PriceTracker")
users = db["users"]
records = db.register



app = Flask(__name__)
app.secret_key = "development"
csrf = CSRFProtect(app)

# @app.after_request
# def add_headers(resp):
#     resp.headers['Content-Security-Policy']='default-src \'self\''
#     return resp

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

@app.route("/items")
def view():
    if not "email" in session:
        return redirect(url_for("index"))

    user_found = users.find_one({"email": session["email"]})    

    
    return render_template("view.html", items=user_found["items"], lists=user_found["lists"])

@app.route("/item/<id>/delete", methods=("POST",))
def delete_item(id):
    if not "email" in session:
        return redirect(url_for("index"))

    users.update_one({"email": session["email"]}, {"$pull": {"items": {"id": id}}})
    return redirect(url_for("view"))

@app.route("/item/<id>/price", methods=("POST",))
def item_price(id):
    if not "email" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        item_date = request.form.get("price-date")
        item_price = request.form.get("price-val")
        new_item_price = {"pid": id + str(random.randrange(300)) , "date": item_date, "price": float(item_price)}
        item_query = {"items.id": id}
        item_update = {"$push": {"items.$.prices": new_item_price}}

        item_add = users.update_one(item_query, item_update)

        return redirect(url_for("item", id=id))

@app.route("/item/<id>", methods=["post", "get"])
def item(id):
    if not "email" in session:
        return redirect(url_for("index"))

    user_found = users.find_one({"email": session["email"]})
    items = user_found["items"]
    item_found = list(filter(lambda item: item["id"] == id, items))
    

    return render_template("item-view.html", item=item_found[0])

@app.route("/item/<id>/edit", methods=("POST",))
def edit(id):
    if not "email" in session:
        return redirect(url_for("index"))

    price_id = request.form.get("priceid")
    update_price = request.form.get("price-edit")

    item_query = {"email": session["email"]}
    

    if "edit" in request.form:
        options = [
            { "i.id": id }, { "p.pid": price_id }
        ]
        item_set = {"$set": {"items.$[i].prices.$[p].price": float(update_price)}}
        item_update = users.update_one(item_query, item_set, array_filters=options)
        return redirect(url_for("item", id=id))

        
    elif "delete" in request.form:
        options = [{"i.id": id}]
        item_pull = {"$pull": {"items.$[i].prices": {"pid": price_id}}}
        item_update = users.update_one(item_query, item_pull, array_filters=options)
        return redirect(url_for("item", id=id))

    
    return redirect(url_for("item", id=id))



    

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

        new_item = {"id": item_name[:4] + str(random.randrange(1,100)), "name": item_name, "sku": item_sku, "desc": item_desc, "prices": []}


        item_query = {"email": session["email"]}
        item_update = {"$push": {"items": new_item}}

        item_add = users.update_one(item_query, item_update)

        return redirect(url_for("hub"))

    return render_template("items.html")

@app.route("/lists")
def lists():
    if not "email" in session:
        return redirect(url_for("index"))

    user_found = users.find_one({"email": session["email"]})

    return render_template("lists.html", lists=user_found["lists"])

@app.route("/lists/add", methods=("POST",))
def add_list():

    if not "email" in session:
        return redirect(url_for("index"))

    list_name = request.form.get("list-name")

    new_list = {"id": list_name[:3] + str(random.randrange(100)), "name": list_name, "items": []}

    list_add = users.update_one({"email": session["email"]}, {"$push": {"lists": new_list}})
    return redirect(url_for("lists"))

@app.route("/lists/<list_id>/addItem/<item_id>")
def add_item_to_list(list_id, item_id):
    if not "email" in session:
        return redirect(url_for("index"))

    user_query = {"email": session["email"]}

    item_found = users.find_one(user_query, {"items.id": 1, "items.name": 1, "_id": 0, "items.prices": 1})


    item_name = ""
    item_price = 0

    for i in item_found["items"]:
        if i["id"] == item_id:
            item_name = i["name"]
            price_list = sorted(i["prices"], key=lambda d: d["date"])
            
            item_price = price_list[-1] if len(price_list) > 0 else 0
            break


    new_item = {"id": item_id, "name": item_name, "qty": 1, "price": item_price, "notes": ""}

    list_query = {"email": session["email"]}
    list_update = {"$push": {"lists.$[i].items": new_item}}
    options = [{"i.id": list_id}]

    item_add = users.update_one(list_query, list_update, array_filters=options)
    return redirect(url_for("view"))

@app.route("/lists/<list_id>/notes/<item_id>", methods=("POST",))
def edit_notes(list_id, item_id):
    if not "email" in session:
        return redirect(url_for("index"))

    item_note = request.form.get("notes")

    user_query = {"email": session["email"]}
    notes_update = {"$set": {"lists.$[i].items.$[t].notes": item_note}}
    options = [
        {"i.id": list_id}, {"t.id": item_id}
    ]

    users.update_one(user_query, notes_update, array_filters=options)
    return redirect(url_for("lists"))

@app.route("/lists/<list_id>/update", methods=("POST", ))
def update_list(list_id):
    if not "email" in session:
        return redirect(url_for("index"))

    item_qty = int(request.form.get("item-qty"))
    item_id = request.form.get("item-id")


    user_query = {"email": session["email"]}

    if item_qty <= 0:
        options = [
            {"i.id": list_id}
        ]
        list_update = {"$pull": {"lists.$[i].items": {"id": item_id}}}
        users.update_one(user_query, list_update, array_filters=options)
        return redirect(url_for("lists"))
        
    if item_qty > 0:
        list_update = {"$set": {"lists.$[i].items.$[t].qty": item_qty}}
        options = [
            {"i.id": list_id}, {"t.id": item_id}
        ]
        users.update_one(user_query, list_update, array_filters=options)

    

    
    
    return redirect(url_for("lists"))

@app.route("/lists/<list_id>/delete")
def delete_list(list_id):
    if not "email" in session:
        return redirect(url_for("index"))

    user_query = {"email": session["email"]}
    list_pull = {"$pull": {"lists": {"id": list_id}}}
    users.update_one(user_query, list_pull)
    return redirect(url_for("lists"))


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
            user_input = {"name": user, "email": email, "password": hashed, "items": [], "lists": []}
            users.insert_one(user_input)
            return redirect(url_for("hub"))

        


    return render_template("register.html")
