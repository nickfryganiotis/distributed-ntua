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
traversed = False
query_sp = 0

def get_url(net):
    return "http://"+net['host']+":"+net['port']


@app.before_first_request
def startup():
  print("Hi asshole")

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

@app.route('/get_identifier',methods = ['GET'])
def _get_identifier():
    global n
    return {'id':n.identifier}

@app.route('/add_songs_to_song_list',methods = ['POST'])
def add_songs_to_song_list():
    global n
    result = request.form.to_dict()
    for key in result:
        n.set_song_to_song_list(int(key),int(result[key]))
    return "Add songs was done"

@app.route('/delete_songs_from_song_list',methods = ['POST'])
def _delete_songs_from_song_list():
    global n
    result = request.form.to_dict()
    for key in result:
        n.delete_song_from_song_list(int(result[key]))
    return "Delete songs was done"

@app.route('/find_successor',methods = ['POST'])
def find_successor():
    global n
    result = request.form.to_dict()
    id = int(result['id'])
    successor_url = get_url(n.get_successor())
    req = requests.get(successor_url+"/get_identifier")
    n_successor_identifier = req.json()['id']
    if  (id > n.identifier and id <= n_successor_identifier) or n_successor_identifier == n.identifier or (n_successor_identifier < n.identifier and id > n.identifier):
        return n.get_successor()
    else:
        req = requests.post(successor_url + "/find_successor", data = {'id':id})
        return req.json()
    return "Error"

@app.route('/join', methods = ['GET'])
def join():
    global n
    global public_net
    global private_net
    hash_index = private_net['host'] + ":"+str(private_net['port'])
    hash_value = hashlib.sha1(hash_index.encode())
    identifier = int(hash_value.hexdigest(),16)
    url = get_url(private_net)
    n = Node(identifier,private_net['host'],private_net['port'])
    if not (private_net['host'] == public_net['host'] and private_net['port'] == public_net['port']):
        res = requests.get(url+"/dht_add_node")
    else:
      n.set_predecessor({'host': n.host,'port': n.port})
      n.set_successor({'host': n.host,'port': n.port})
    return "Join was Successful"
@app.route('/dht_add_node',methods = ['GET'])
def dht_add_node():
    global n
    global public_net
    public_url = get_url(public_net)
    req = requests.post(public_url+"/find_successor",data = {'id':n.identifier})
    n_successor = req.json()
    n.set_successor(n_successor)
    successor_url = get_url(n_successor)
    req = requests.get(successor_url+"/get_predecessor")
    n_predecessor = req.json()
    n.set_predecessor(n_predecessor)
    req = requests.post(successor_url+"/set_predecessor",data = {'host': n.host, 'port': n.port})
    predecessor_url = get_url(n_predecessor)
    req = requests.post(predecessor_url+"/set_successor",data = {'host': n.host, 'port': n.port})
    req = requests.get(successor_url+"/get_song_list")
    successor_song_list = req.json()
    deleted_keys = {}
    for key in successor_song_list:
        if key <= n.identifier:
            n.set_song_to_song_list(key,successor_song_list[key])
            deleted_keys[key] = ""
    req = requests.post(successor_url+"/delete_songs_from_song_list",data = deleted_keys)
    return "Add node to dht successfully done"

@app.route('/insert',methods = ['POST'])
def insert():
  global n
  global private_net
  results = request.form.to_dict()
  key = int(results['key'])
  value = int(results['value'])
  url = get_url(private_net)
  req = requests.post(url+"/find_successor",data = {'id': key})
  id_successor = req.json()
  successor_url = get_url(id_successor)
  req = requests.post(successor_url+"/add_songs_to_song_list", data = {key:value})
  return "Insert done"

@app.route('/delete',methods = ['POST'])
def delete():
  global n
  global private_net
  results = request.form.to_dict()
  key = int(results['key'])
  url = get_url(private_net)
  req = requests.post(url+"/find_successor",data = {'id': key})
  id_successor = req.json()
  successor_url = get_url(id_successor)
  req = requests.post(successor_url+"/delete_songs_from_song_list",data = {'key': key})
  return "Delete done"

@app.route('/query',methods = ['POST'])
def query():
  global n
  global query_sp
  global traversed
  global private_net
  results = request.form.to_dict()
  key = int(results['key'])
  url = get_url(private_net)
  if not key == query_sp:
    req = requests.post(url+"/find_successor", data = {'id':key})
    id_successor = req.json()
    successor_url = get_url(id_successor)
    req = requests.get(successor_url+"/get_song_list")
    return {'value': req.json()[str(key)]}
  else:
    text = ""
    if not traversed:
      text = "Node " +str(n.identifier)+":\n" 
      tmp_song_list = n.get_song_list()
      for key in tmp_song_list:
        text += "key: "+str(key)+" value: "+str(tmp_song_list[key])+"\n"
      n_successor = n.get_successor()
      successor_url = get_url(n_successor)
      traversed = True
      req = requests.post(successor_url+'/query',data = {'key':query_sp})
      text += req.text
      traversed = False
    return text
  return "Query done"

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

@app.route('/overlay',methods = ['GET'])
def overlay():
    global n
    global traversed
    text = ""
    if not traversed:
        text = "Node "+str(n.identifier)+" -> "
        n_successor = n.get_successor()
        successor_url = get_url(n_successor)
        traversed = True
        req = requests.get(successor_url+"/overlay")
        text += req.text
        traversed = False
    return text



@app.route('/help',methods = ['GET'])
def help():
    text = "CLI Commands: \n"
    text += "   insert <key> <value>  Inserts new (key,value) pair, where key is a song title and value is the name of the node where one must connect to download the song\n"
    text += "   delete <key>          Deletes (key,value) pair, where key is a song title\n"
    text += "   query <key>           Searches DHT for (key,value) pair given a key argument, which is a song title and returns its corresponding value\n"
    text += "   query *               Returns every (key,value) pair in the DHT, groupped by the node containing it\n"
    text += "   depart                Graceful departure of current node\n"
    text += "   overlay               Shows the current DHT topology\n"
    return text

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