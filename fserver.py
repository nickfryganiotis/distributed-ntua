from flask import Flask, render_template, request
import requests
import sys
from node2 import Node
import hashlib
import json

app = Flask(__name__)
public_net= {}
public_net['host'] = "192.168.0.1"
public_net['port'] = "5000"
private_net = {}
n = None
traversed = False
query_sp = 0
k = 0
replication_method = ""

def get_url(net):
    return "http://"+net['host']+":"+net['port']


@app.before_first_request
def startup():
  print("Hi asshole")

# Node methods

### Setters

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

#@app.route('/set_replication_parameters',methods = ['POST'])
#def _set_replication_parameters():
#    global k
#    global replication_method
#    result = request.form.to_dict()
#    k = int(result['k'])
#    replication_method = result['replication_method']
#    return "Set replication parameters done"

### Getters

@app.route('/get_predecessor',methods = ['GET'])
def _get_predecessor():
    global n
    return n.get_predecessor()

@app.route('/get_successor', methods = ['GET'])
def _get_successor():
    global n
    return n.get_successor()

@app.route('/get_song_list',methods = ['GET'])
def _get_song_list():
    global n
    return n.get_song_list()
@app.route('/get_replica_list',methods = ['GET'])
def _get_replica_list():
    global n
    return n.get_replica_list()

@app.route('/get_identifier',methods = ['GET'])
def _get_identifier():
    global n
    return {'id':n.identifier}

@app.route('get_replication_parameters')
def _get_replication_parameters():
    global k
    global replication_method
    return {'k':k,'replication_method':replication_method}

### Add elements

@app.route('/add_songs_to_song_list',methods = ['POST'])
def add_songs_to_song_list():
    global n
    result = request.form.to_dict()
    for key in result:
        n.set_song_to_song_list(int(key),int(result[key]))
    return "Add songs was done"

@app.route('/add_replicas_to_song_list', methods = ['POST'])
def add_replicas_to_song_list():
    global n
    result = requests.form.to_dict()
    replicas = json.loads(result['replicas'])
    for key in replicas:
        n.set_replica_to_replica_list(int(key),replicas[key])
    return "Add replica was done"   

### Delete elements

@app.route('/delete_songs_from_song_list',methods = ['POST'])
def _delete_songs_from_song_list():
    global n
    result = request.form.to_dict()
    for key in result:
        n.delete_song_from_song_list(int(key))
    return "Delete songs was done"

# Chord methods

@app.route('/find_successor',methods = ['POST'])
def find_successor():
    global n
    result = request.form.to_dict()
    id = int(result['id'])
    successor_url = get_url(n.get_successor())
    req = requests.get(successor_url+"/get_identifier")
    n_successor_identifier = req.json()['id']
    if  (id > n.identifier and id <= n_successor_identifier) or n_successor_identifier == n.identifier or (n_successor_identifier < n.identifier and (id > n.identifier or id < n_successor_identifier)):
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
    if not (private_net['host'] == public_net['host'] and private_net['port'] == public_net['port']):
        ## Initialize Node different from the Coordinator
        res = requests.get(url+"/dht_add_node")
    else:
      ## Initialize Coordinator
      n.set_predecessor({'host': n.host,'port': n.port})
      n.set_successor({'host': n.host,'port': n.port})
    return "Join was Successful"

@app.route('/dht_add_node',methods = ['GET'])
def dht_add_node():
    global n
    global public_net
    global k
    global replication_method
    global traversed 
    
    ## Coordinator finds new Node's successor
    public_url = get_url(public_net)
    req = requests.post(public_url+"/find_successor",data = {'id':n.identifier})
    n_successor = req.json()
    n.set_successor(n_successor)
    successor_url = get_url(n_successor)

    ## New Node's predecessor is the predecessor of the successor 
    req = requests.get(successor_url+"/get_predecessor")
    n_predecessor = req.json()
    n.set_predecessor(n_predecessor)

    ## New successor of successor's predecessor is the new Node
    req = requests.post(successor_url+"/set_predecessor",data = {'host': n.host, 'port': n.port})
    predecessor_url = get_url(n_predecessor)
    req = requests.post(predecessor_url+"/set_successor",data = {'host': n.host, 'port': n.port})
    req = requests.get(successor_url+"/get_song_list")
    
    ## Νew Node song list is successor's song list for keys that hash(key) <= Node identifier
    successor_song_list = req.json()
    deleted_keys = {}
    for key in successor_song_list:
        if int(key) <= n.identifier:
            n.set_song_to_song_list(int(key),int(successor_song_list[key]))
            deleted_keys[key] = ""
    
    ## Successor deletes the songs that belong to me
    req = requests.post(successor_url+"/delete_songs_from_song_list",data = deleted_keys)

    ## Coordinator gives replication parameters to Node
    req = requests.get(public_url+"/get_replication_parameters")
    replication_parameters = req.json()
    k = int(replication_parameters['k'])
    replication_method = replication_parameters['replication_method']
    
    ## In case of k > 1 new Node gets replicas of predecessor if replica chain doesn't stop on predecessor  
    if not k == 1:
        req = requests.get(predecessor_url+"/get_replica_list")
        predecessor_replica_list = req.json()
        for key in predecessor_replica_list:
            val_arr = predecessor_replica_list[key]
            if val_arr[1] < k-1:
                n.set_replica_to_replica_list(int(key),[val_arr[0],val_arr[1]+1])
        traversed = True
        ## New Node exchanges replicas with his successor
        req = requests.post(successor_url+"replicas_exchange_after_join",data = {'replicas':json.dumps(n.get_replica_list)})
        traversed = False
    return "Add node to dht successfully done"

@app.route('/replicas_exchange_after_join', methods = ['POST'])
def replicas_exchange_after_join():
    global n
    global traversed
    global k
    global private_net

    if not traversed:
        result = request.form.to_dict()
        new_node_replicas = json.load(result['replicas'])
        end_replicas_exchange = True
        ## Check if replica chain has been completed for every replica of new Node
        for key in new_node_replicas:
            val_arr = new_node_replicas[key]
            end_replicas_exchange = end_replicas_exchange and (val_arr[1] == k)
            if not end_replicas_exchange:
                break
        if end_replicas_exchange:
            traversed = False
            return "Replicas exchange after join successfully done"
        
        replicas_exchange = {}
        tmp_node_replicas = n.get_replica_list()
        for key in new_node_replicas:
            val_arr = new_node_replicas[key]
            ## If replica chain has finished to tmp_node predecessor delete replica
            if int(key) in tmp_node_replicas:
                if val_arr[1] == k-1:
                    n.delete_replica_from_replica_list(int(key))
                else:
                    n.set_replica_to_replica_list(int(key),val_arr[1]+1)
                val_arr[1] += 1
            replicas_exchange[int(key)] = val_arr
        
        ## Tmp_node exchanges replicas with his successor
        successor_url = get_url(n.get_successor())
        traversed = True
        req = requests.post(successor_url+"/replicas_exchange_after_join",data = {'replicas':json.dumps(replicas_exchange)})
    traversed = False
    return "Replicas exchange after join successfully done" 

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
  req = requests.post(successor_url+"/delete_songs_from_song_list",data = {key: ''})
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
    global k
    global traversed
    n_successor = n.get_successor()
    successor_url = get_url(n_successor)
    n_predecessor = n.get_predecessor()
    predecessor_url = get_url(n_predecessor)
    ## New predecessor of leaving Node's successor is leaving Node's predecessor
    req = requests.post(successor_url+"/set_predecessor",data = n_predecessor)
    ## New successor of leaving Node's predecessor is leaving Node's successor
    req = requests.post(predecessor_url+"/set_successor",data = n_successor)
    ## Leaving Node gives his song list to his successor
    req = requests.post(successor_url+"/add_songs_to_song_list",data = n.get_song_list())
    
    ## In case of k > 1 leaving Node gives his replicas to his successor
    if not k == 1:
        traversed = True
        req = requests.post(successor_url+"replicas_exchange_after_depart",data = {'replicas':json.dumps(n.get_replica_list)})
        traversed = False
    n = None
    return "Depart node successfuly done"

@app.route('/replicas_exchange_after_depart',methods = ['POST'])
def replicas_exchange_after_depart():
    global n
    global k
    global traversed

    if not traversed:
        result = request.form.to_dict()
        leaving_node_replicas = json.load(result['replicas'])
        ## Check if leaving Node has delivered all of his replicas
        if not leaving_node_replicas:
            traversed = False
            return "Replicas exchange after depart successfully done"
        
        tmp_node_replicas = n.get_replica_list()
        replicas_exchange = {}
        for key in leaving_node_replicas:
            val_arr = leaving_node_replicas[key]
            ## Leaving node delivers his replica to tmp_node and tmp_node deletes his replica with the same hash(key) if it exists 
            n.set_replica_to_replica_list(int(key),val_arr[1])
            # If tmp_node replica list does't contain a replica with the same id, it means that replica chain stops on tmp_node 
            if int(key) in tmp_node_replicas:
                replicas_exchange[int(key)] = val_arr
        ## Tmp_node exchanges replicas with his successor
        successor_url = get_url(n.get_successor())
        traversed = True
        req = requests.post(successor_url+"/replicas_exchange_after_depart",data = {'replicas':json.dumps(replicas_exchange)})
    traversed = False
    return "Replicas exchange after join successfully done" 


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