from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from schema import schema

app = Flask(__name__)
app.debug = True

CORS(app)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
                                                           schema=schema,
                                                           graphiql=True,
                                                           ))


@app.route('/')
@app.route('/home')
def home():
    return 'Hi'


if __name__ == '__main__':
    app.run()