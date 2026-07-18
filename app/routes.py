from app import app

@app.route("/")
def home():
    return "VB Stock Manager is Running!"
