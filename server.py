from flask import Flask, render_template, request
import requests
import sys
from node import Node
from finger import Finger
import hashlib

public = {}
public['ip'] = "192.168.0.1"
public['port'] = 5000
n = None
app = Flask(__name__)

@app.before_first_request
def startup():
  print("Hi nick")
@app.route('/get_node',methods = ['GET'])
def get_node():
  return n
@app.route('/set_predecessor',methods = ['POST'])
def set_predecessor():
  result = request.form.to_dict()
  nn = results['nn']
  n.set_predecessor(nn)
@app.route('/find_successor',methods = ['POST'])
def find_successor():
  result = request.form.to_dict()
  id = result['id']
  nn = requests.post(n.get_url()+"/find_predecessor",data = {'id': id})
  return nn

@app.route('/find_predecessor',methods = ['POST'])
def find_predecessor():
  results = request.form.to_dict()
  id = results['id']
  nn = n
  while not (id > nn.identifier and id < nn.get_finger_table()[0].get_node()):
    nn = requests.post(nn.get_url()+"/closest_preceding_finger",data = {'id': id})
  return nn

@app.route('/closest_preceding_finger', methods = ['POST'])
def closest_preceding_finger():
  results = request.form.to_dict()
  id = results['id']
  for i in range(159,-1,-1):
    if n.get_finger_table()[i].get_node().identifier > n.identifier and n.get_finger_table()[i].get_node().identifier < id :
      return n.get_finger_table()[i].get_node()
  return n
@app.route('/join',methods = ['GET'])
def join():
  for i in range(160):
    f = Finger(n.identifier,i)
    n.add_finger_to_finger_table(f)
  if not n.coordinator:
    nn = requests.get("http://"+public['ip']+":"+str(port)+"/get")
    tmp = requests.post(n.get_url()+"/init_finger_table",data = nn)
    tmp = requests.post(n.get_url()+"/update_others")
  else:
    n.set_predecessor(n)
    for i in range(160):
      n.get_finger_table()[i].set_node = n
  return n
@app.route('/init_finger_table',methods = ['POST'])
def init_finger_table():
  results = request.form.to_dict()
  nn = results['node']
  id = nn.get_finger_table()[0].start
  nn = requests.post(nn.get_url()+"/find_successor",data = {'id': id})
  n.set_node_finger_table(0,nn)
  n.set_predecessor(n.get_finger_table()[0].get_node().get_predecessor())
  nn.set_predecessor(n)
  req = requests.post(nn.get_url()+"/set_predecessor", data = n)
  for i in range(159):
     if n.get_finger_table()[i+1].start() >= n.identifier and n.get_finger_table[i+1].start() < n.get_finger_table[i].get_node().identifier:
        n.set_node_to_finger_table(i+1,n.get_finger_table()[i].get_node())
     else:
       nn = requests.get(nn.get_url()+"/find_successor",data = {'id': nn.get_finger_table()[i+1].start})
       n.set_node_to_finger_table(i+1,nn)

@app.route('/add_to_song_list',methods = ['POST'])
def add_to_song_list():
  results = request.form.to_dict()
  key = results['key']
  value = results['value']
  n.add_to_song_list(key,value)
@app.route('/insert',methods = ['POST'])
def insert():
  results = request.form.to_dict()
  key = results['key']
  value = results['value']
  nn = requests.post(n.get_url()+"/find_successor",data = {'id': key})
  req = requests.post(nn.get_url+"/add_to_song_list", data = {'key': key , 'value': value})


@app.route('/delete_from_song_list',methods = ['POST'])
def delete_from_song_list():
  results = request.form.to_dict()
  key = results['key']
  n.delete_from_song_list(key)

@app.route('/delete',methods = ['POST'])
def delete():
  results = request.form.to_dict()
  key = results['key']
  nn = requests.post(n.get_url()+"/find_successor",data = {'id': key})
  req = requests.post(nn.get_url+"/delete_from_song_list",data = {'key': key})


def main(host,port):
  hash_index = host + ":"+str(port)
  hash_value = hashlib.sha1(hash_index.encode())
  identifier = int(hash_value.hexdigest(),16)
  global n
  n = Node(identifier,host,port)
  app.run(host = host,port = port,debug = True,use_reloader = False)

if __name__ == '__main__':
  host = sys.argv[1]
  port = int(sys.argv[2])
  main(host,port)