from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView

app = Flask(__name__)
app.debug = True

CORS(app)

@app.route('/')
@app.route('/home')
def home():
    return 'Hi'

if __name__ == '__main__':
    app.run()