import flask from Flask

def startWebserver():
    app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify(result='Hello World')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")