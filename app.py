from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
#page d'accuil
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    question = request.form['question']
    return render_template('response.html', question=question)

# page hypotetique pour recuil de une reponse 
@app.route('/reponse')
def reponse():
    return render_template('response.html')

#page qcm
@app.route('/qcm')
def qcm():
    return render_template('qcm.html')

#page challenge
@app.route('/challenge')
def challenge():
    return render_template('challenge.html')

if __name__ == '__main__':
    app.run(debug=True)

