

from flask import Flask, request,jsonify,render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/')
def introduce():
    return render_template('traffic.html')


if __name__ == "__main__":
    app.run(debug=True)
# host = '0.0.0.0',port='5000'