from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", dimensions=dimensions)

if __name__ == "__main__":
    dimensions = 10 
    app.run(debug=True) 