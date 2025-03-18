from flask import Flask
from controllers import controllers

app = Flask(__name__)
app.register_blueprint(controllers)

if __name__ == '__main__':
    app.run(debug=True)