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
if __name__=="__main__":
    app.run(debug=True)