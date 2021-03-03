from flask import Flask, render_template, request
import sys
import hashlib

app = Flask(__name__)
publicPort = 5000
privatePort = publicPort
coordinator = False
numberOfNodes = 1
songs = []

@app.route('/',methods = ['GET','POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html',port = privatePort)
    if request.method == 'POST':
        print(privatePort)
        return render_template('user.html')
@app.route('/insert',methods = ['POST', 'GET'])
def insert():
    if request.method == 'GET':
        return render_template('user.html')
    if request.method == 'POST':
        result: None = request.form.to_dict()
        print(result)
        return render_template('user.html', port = privatePort)

def main(port):
    publicPort = port
    global privatePort
    privatePort = publicPort
    if privatePort == publicPort:
        coordinator = True
    app.run(port = port,debug=True)

if __name__ == '__main__':
    main(int(sys.argv[1]))
