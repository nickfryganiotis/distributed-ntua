from flask import Flask, render_template, request,json
import requests
import sys
from node import Node
from finger import Finger
import hashlib

app = Flask(__name__)
public_net= {}
public_net['host'] = "192.168.0.1"
public_net['port'] = 5000
private_net = {}
visited_nodes = {}
n = None
m = 160
traversed = False
query_sp = 0

class Object:
  def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)                                                                                                                                 
def create_node(res):
 n = Node(res['identifier'],res['host'],res['port'])
 n.set_predecessor(res['predecessor']['host'],res['predecessor']['port'])
 for f in res['finger_table']:
   ff = Finger(f['identifier'],f['index'])
   ff.set_node(f['_node_url']['host'],f['_node_url']['port'])
   n.add_finger_to_finger_table(ff)
 return n

def _get_node(n):
  me = {}
  me['identifier'] = n.identifier
  me['host'] = n.host
  me['port'] = n.port
  finger_obj = Object()
  finger_obj.finger_table = n.get_finger_table()
  finger_table = finger_obj.toJSON()
  me['finger_table'] = json.loads(finger_table)['finger_table']
  me['predecessor'] = n.get_predecessor()
  return me


@app.before_first_request
def startup():
  print("Hi nick")

@app.route('/get_node',methods = ['GET'])
def get_node():
  global n
  return _get_node(n)

@app.route('/set_predecessor',methods = ['POST'])
def set_predecessor():
  global n
  result = request.form.to_dict()
  n.set_predecessor(result['host'],int(result['port']))
  return _get_node(n)

@app.route('/find_successor',methods = ['POST'])
def find_successor():
  global n
  result = request.form.to_dict()
  id = int(result['id'])
  res = requests.post(n.get_url()+"/find_predecessor",data = {'id': id})
  nn = create_node(res.json())
  successor_url = nn.get_finger_table()[0].get_node()
  res = requests.get("http://"+successor_url['host']+":"+str(successor_url['port'])+"/get_node")
  nn_successor = create_node(res.json())
  return _get_node(nn_successor)

@app.route('/find_predecessor',methods = ['POST'])
def find_predecessor():
  global n
  #global visited_nodes
  results = request.form.to_dict()
  id = int(results['id'])
  nn = n
  #visites_nodes = {}
  successor_url = nn.get_finger_table()[0].get_node()
  #if (successor_url['host']+":"+str(successor_url['port'])) in visited_nodes:
  #  nn_successor = visited_nodes[successor_url['host']+":"+str(successor_url['port'])]
  #else:
  res = requests.get("http://"+successor_url['host']+":"+str(successor_url['port'])+"/get_node")
  nn_successor = create_node(res.json())
    #visited_nodes[successor_url['host']+":"+str(successor_url['port'])] = nn_successor
  while (not id > nn.identifier and id <= nn_successor.identifier) and (not nn.identifier == nn_successor.identifier) :
    #if (nn.host+":"+str(nn.port)) in visites_nodes:
      #nn = visites_nodes[nn.host+":"+str(nn.port)]
    #else:
    res =  requests.post(nn.get_url()+"/closest_preceding_finger",data = {'id': id})
    nn = create_node(res.json())
      #visites_nodes[nn.host+":"+str(nn.port)] = nn
    successor_url = nn.get_finger_table()[0].get_node()
    #if (successor_url['host']+":"+str(successor_url['port'])) in visited_nodes:
     # nn_successor = visited_nodes[successor_url['host']+":"+str(successor_url['port'])]
    #else:
    res = requests.get("http://"+successor_url['host']+":"+str(successor_url['port'])+"/get_node")
    nn_successor = create_node(res.json())
      #visited_nodes[successor_url['host']+":"+str(successor_url['port'])] = nn_successor
  return _get_node(nn)

@app.route('/closest_preceding_finger', methods = ['POST'])
def closest_preceding_finger():
  global n
  global m
  #global visited_nodes
  results = request.form.to_dict()
  id = int(results['id'])
  for i in range(m-1,-1,-1):
    node_url = n.get_finger_table()[i].get_node()
    #if (node_url['host']+":"+str(node_url['port'])) in visited_nodes:
     # finger_i_node = visited_nodes[node_url['host']+":"+str(node_url['port'])]
    #else:
    res = requests.get("http://"+node_url['host']+":"+str(node_url['port'])+"/get_node")
    finger_i_node = create_node(res.json())
      #visited_nodes[node_url['host']+":"+str(node_url['port'])] = finger_i_node

    if (finger_i_node.identifier > n.identifier and finger_i_node.identifier < id) or (finger_i_node.identifier == n.identifier):
      return _get_node(finger_i_node)
  return _get_node(n)

@app.route('/join',methods = ['GET'])
def join():
  global n
  global public_net
  global private_net
  global m
  hash_index = private_net['host'] + ":"+str(private_net['port'])
  hash_value = hashlib.sha1(hash_index.encode())
  identifier = int(hash_value.hexdigest(),16)
  n = Node(identifier,private_net['host'],private_net['port'])
  for i in range(m):
    f = Finger(n.identifier,i)
    n.add_finger_to_finger_table(f)
  if not (private_net['host'] == public_net['host'] and private_net['port'] == public_net['port']):
    res = requests.get(n.get_url()+"/init_finger_table")
    res = requests.get(n.get_url()+"/update_others")
  else:
    for i in range(m):
      n.get_finger_table()[i].set_node(n.host,n.port)
    n.set_predecessor(n.host,n.port)
  return _get_node(n)

@app.route('/init_finger_table',methods = ['GET'])
def init_finger_table():
  global n
  global m
  global public_net
  res =  requests.post("http://"+public_net['host']+":"+str(public_net['port'])+"/find_successor",data = {'id':n.get_finger_table()[0].start()})
  n_successor = create_node(res.json())
  n.get_finger_table()[0].set_node(n_successor.host,n_successor.port)
  n.set_predecessor(n_successor.get_predecessor()['host'],n_successor.get_predecessor()['port'])
  res = requests.post(n_successor.get_url()+"/set_predecessor",data = {'host':n.host,'port':n.port})
  for i in range(m-1):
     node_url = n.get_finger_table()[i].get_node()
     res = requests.get("http://"+node_url['host']+":"+str(node_url['port'])+"/get_node")
     finger_i_node = create_node(res.json())
     if n.get_finger_table()[i+1].start() >= n.identifier and n.get_finger_table()[i+1].start() < finger_i_node.identifier:
        n.get_finger_table()[i+1].set_node(n.get_finger_table()[i].get_node()['host'],n.get_finger_table()[i].get_node()['port'])
     else:
       res = requests.post("http://"+public_net['host']+":"+str(public_net['port'])+"/find_successor",data = {'id':n.get_finger_table()[i+1].start()})
       res_node = create_node(res.json())
       n.get_finger_table()[i+1].set_node(res_node.host,res_node.port)
  return _get_node(n)

@app.route('/update_finger_table',methods = ['POST'])
def update_finger_table():
  global n
  results = request.form.to_dict()
  res = requests.get("http://"+results['host']+":"+results['port']+"/get_node")
  s = create_node(res.json())
  i = int(results['index'])
  node_url = n.get_finger_table()[i].get_node()
  res = requests.get("http://"+node_url['host']+":"+str(node_url['port'])+"/get_node")
  finger_i_node = create_node(res.json())
  if (s.identifier >= n.identifier and s.identifier < finger_i_node.identifier) and not (n.identifier == finger_i_node.identifier):
    n.get_finger_table()[i].set_node(s.host,s.port)
    predecessor_url = n.get_predecessor()
    res = requests.post("http://"+predecessor_url['host']+":"+str(predecessor_url['port'])+"update_finger_table",data = {'host':s.host,'port':s.port,'index':i})
  return _get_node(n)

@app.route('/update_others',methods = ['GET'])
def update_others():
  global n
  global m
  for i in range(m):
    res = requests.post(n.get_url()+"/find_predecessor",data = {'id': (n.identifier-2**i)})
    p = create_node(res.json())
    res = requests.post(p.get_url()+"/update_finger_table",data = {'host':n.host,'port':n.port,'index':i})
  return _get_node(n)

@app.route('/add_to_song_list',methods = ['POST'])
def add_to_song_list():
  global n
  results = request.form.to_dict()
  key = int(results['key'])
  value = int(results['value'])
  n.add_to_song_list(key,value)
  return _get_node(n)
@app.route('/insert',methods = ['POST'])
def insert():
  global n
  results = request.form.to_dict()
  key = int(results['key'])
  value = int(results['value'])
  req = requests.post(n.get_url()+"/find_successor",data = {'id': key})
  nn = create_node(req.json())
  req = requests.post(nn.get_url()+"/add_to_song_list", data = {'key': key , 'value': value})
  return _get_node(n)


@app.route('/delete_from_song_list',methods = ['POST'])
def delete_from_song_list():
  global n
  results = request.form.to_dict()
  key = int(results['key'])
  n.delete_from_song_list(key)
  return _get_node(n)

@app.route('/delete',methods = ['POST'])
def delete():
  global n
  results = request.form.to_dict()
  key = int(results['key'])
  req = requests.post(n.get_url()+"/find_successor",data = {'id': key})
  nn = create_node(req.json())
  req = requests.post(nn.get_url+"/delete_from_song_list",data = {'key': key})
  return _get_node(n)
@app.route('/query',methods = ['POST'])
def query():
  global n
  global query_sp
  global traversed
  results = request.form.to_dict()
  key = int(results['key'])
  if not key == query_sp:
    req = requests.post(n.get_url()+"/find_successor", data = {'id':key})
    nn = create_node(req.json())
    return {'value': nn.get_song_list()[key]}
  else:
    if not traversed:
      f = open("query.txt","w")
      f.write("Node "+str(n.identifier)+":\n")
      tmp_song_list = n.get_song_list()
      for key in tmp_song_list:
        f.write("key: "+str(key)+" value: "+str(tmp_song_list[key])+"\n")
      f.close()
      successor_url = n.get_finger_table()[0].get_node()
      traversed = True
      req = requests.post("http://"+successor_url['host']+":"+str(successor_url['port'])+'/query',data = {'key':query_sp})
      traversed = False
    return {}
  return {}

@app.route('/dfs',methods = ['GET'])
def dfs():
  global traversed
  if traversed:
    return "traversed"
  else:
    f = open("overlay.txt","w")

@app.route('/overlay',methods = ['GET'])
def overlay():
  global public_net
  req = requests.get("http:"+public_net['host']+":"+public_net['port']+"/dfs")
  return "overlay"



def main(host,port):
  global private_net
  global query_sp
  sp = "*"
  hash_value = hashlib.sha1(sp.encode())
  query_sp = int(hash_value.hexdigest(),16)
  private_net['host'] = host
  private_net['port'] = port
  app.run(host = host,port = port,debug = True,use_reloader = False)

if __name__ == '__main__':
  host = sys.argv[1]
  port = int(sys.argv[2])
  main(host,port)