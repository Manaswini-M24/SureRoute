from flask import Flask,render_template,request,jsonify
app=Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/driver")
def driver():
    return render_template("driver.html")
@app.route("/passenger")
def passenger():
    return render_template("passenger.html")
@app.route("/signup",methods=["POST"])
def signup():
    full_name=request.form.get("full_name")
    email=request.form.get("email")
    password=request.form.get("password")
    bus_name=request.form.get("bus_name")
    bus_number=request.form.get("bus_number")
    bus_route=request.form.get("bus_route")
    bus_timings=request.form.get("bus_timings")
    # if valid():
    return jsonify({"status": "success", "message": "Driver account created. Please log in."})
    # else:
    # return jsonify({"status": "error", "message": "Invalid login"})
@app.route("/login",methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "driver" and password == "1234":
        return jsonify({"status": "success", "message": "Welcome back, Driver!"})
    else:
        return jsonify({"status": "error", "message": "Invalid login"})
if __name__=="__main__":
    app.run(debug=True)