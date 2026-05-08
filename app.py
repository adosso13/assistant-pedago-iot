from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/qcm')
def qcm():
    return render_template('qcm.html')

@app.route('/challenge')
def challenge():
    return render_template('challenge.html')

"""
@app.route('/challenge/theme1')
def theme1():
    return render_template('theme1.html')
"""

if __name__ == '__main__':
    app.run(debug=True)

