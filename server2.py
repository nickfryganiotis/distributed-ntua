from flask import Flask, render_template, request,json
import requests
import sys
from node2 import Node
import hashlib

app = Flask(__name__)
public_net= {}
public_net['host'] = "192.168.0.1"
public_net['port'] = "5000"
private_net = {}
n = None
query_sp = 0

def get_url(net):
    return "http:"+net['host']+":"+net['port']
@app.route('/set_predecessor',methods = ['POST'])
def _set_predecessor():
    global n
    result = request.form.to_dict()
    n.set_predecessor(result)
    return "Set predecessor done"

@app.route('/get_predecessor',methods = ['GET'])
def _get_predecessor():
    global n
    return n.get_predecessor()

@app.route('/join', methods = ['GET'])
def join():
    global n                                                                                                                
    global public_net
    global private_net 
    hash_index = private_net['host'] + ":"+str(private_net['port'])
    hash_value = hashlib.sha1(hash_index.encode())                                                                          
    identifier = int(hash_value.hexdigest(),16)
    n = Node(identifier,private_net['host'],private_net['port'])
    if not (private_net['host'] == public_net['host'] and private_net['port'] == public_net['port']):
        res = requests.get(n.get_url()+"/init_node")
        res = requests.get(n.get_url()+"/update_others")
    else:
      n.set_predecessor({'host': n.host,'port': n.port})
      n.set_successor({'host': n.host,'port': n.port})
@app.route('/init_node',methods = ['GET'])
def init_node():
    global n
    global public_net
    public_url = get_url(public_net)
    n_successor = requests.post(public_url+"/find_successor",data = {'id':n.identifier})
    n.set_successor(n_successor)
    n_predecessor = request.get(public_url+"/get_predecessor")
    n.set_predecessor(n_predecessor)
    req = requests.post(public_url+"/set_predecessor",data = {'host':n.host,'port':n.port})
    

def main(host,port):
  global private_net
  global query_sp
  sp = "*"
  hash_value = hashlib.sha1(sp.encode())
  query_sp = int(hash_value.hexdigest(),16)
  private_net['host'] = host
  private_net['port'] = port
  app.run(host = host,port = int(port),debug = True,use_reloader = False)

if __name__ == '__main__':
  host = sys.argv[1]
  port = sys.argv[2]
  main(host,port)