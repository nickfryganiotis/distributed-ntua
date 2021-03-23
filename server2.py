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

@app.route('/set_successor',methods = ['POST'])
def _set_successor():
    global n
    result = request.form.to_dict()
    n.set_successor(result)
    return "Set successor done"

@app.route('/get_predecessor',methods = ['GET'])
def _get_predecessor():
    global n
    return n.get_predecessor()

@app.route('/get_song_list',methods = ['GET'])
def _get_song_list():
    global n
    return n.get_song_list()

#@app.route('/get_identifier',methods = ['GET'])
#def _get_identifier():
#    global n
#    return {'id':n.identifier}

@app.route('/add_songs_to_song_list',methods = ['POST'])
def add_songs_to_song_list():
    global n
    result = request.form_to_dict()
    for key in result:
        n.set_song_to_song_list(int(key),int(result[key]))
    return "Add songs was done"

@app.route('/delete_songs_from_song_list',methods = ['POST'])
def _delete_songs_from_song_list():
    global n
    result = request.form.to_dict()
    for key in result:
        n.delete_song_from_song_list(int(key))
    return "Delete songs was done"

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
        res = requests.get(n.get_url()+"/dht_add_node")
    else:
      n.set_predecessor({'host': n.host,'port': n.port})
      n.set_successor({'host': n.host,'port': n.port})

@app.route('/dht_add_node',methods = ['GET'])
def dht_add_node():
    global n
    global public_net
    public_url = get_url(public_net)
    n_successor = requests.post(public_url+"/find_successor",data = {'id':n.identifier})
    n.set_successor(n_successor)
    successor_url = get_url(n_successor)
    n_predecessor = request.get(successor_url+"/get_predecessor")
    n.set_predecessor(n_predecessor)
    req = requests.post(successor_url+"/set_predecessor",data = {'host': n.host, 'port': n.port})
    predecessor_url = get_url(n_predecessor)
    req = requests.post(predecessor_url+"/set_suceessor",data = {'host': n.host, 'port': n.port})
    successor_song_list = (successor_url+"/get_song_list")
    deleted_keys = {}
    for key in successor_song_list:
        if key <= n.identifier:
            n.set_song_to_song_list(key,successor_song_list[key])
            deleted_keys[key] = ""
    req = requests.post(successor_url+"/delete_songs_from_song_list",data = deleted_keys) 
    return "Add node to dht successfully done"

@app.route('/depart',methods = ['GET'])
def depart():
    global n
    n_successor = n.get_successor()
    successor_url = get_url(n_successor)
    n_predecessor = n.get_predecessor()
    predecessor_url = get_url(n_predecessor)
    req = requests.post(successor_url+"/set_predecessor",data = n_predecessor)
    req = requests.post(predecessor_url+"/set_successor",data = n_successor)
    req = requests.post(successor_url+"/add_songs_to_song_list",data = n.get_song_list())
    n = None
    return "Depart node successfuly done"

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