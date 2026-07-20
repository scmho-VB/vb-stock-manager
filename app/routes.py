from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "VB Stock Manager is Running!"
