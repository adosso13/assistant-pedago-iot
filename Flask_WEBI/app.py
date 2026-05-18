from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
#page d'accueil
def home():
    return 'Hello'

if __name__ == '__main__':
    app.run(debug=True)

