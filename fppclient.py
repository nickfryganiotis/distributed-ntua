import sys
import os
import requests
import hashlib
import json

public_net = {}
public_net['host'] = "192.168.0.1"
public_net['port'] = "5000"
private_net = {}

def get_url(net):
    return "http://"+net['host']+":"+net['port']


def insert_eventual_consistency(url,key_identifier,value_identifier,k):
  req = requests.post(url+"/find_successor", data = {'id' : key_identifier})
  primary_node = req.json()
  #primary_node_url = get_url(primary_node)
  successor_url = get_url(primary_node)
  for i in range(2,k+1):
    req = requests.get(successor_url+"/get_successor")
    successor = req.json()
    if successor == primary_node:
      break
    successor_url = get_url(successor)
    req = requests.post(successor_url + "/add_replicas_to_replica_list", data = {'replicas':json.dumps({key_identifier:[value_identifier,i-1]})})
  return

def query_eventual_consistency(url,key_identifier):
   ## Default answer if none of Nodes owns this key

   answer = {}
   answer['key'] = "Not found"
   ## Check if Node's song_list contains this key
   successor_url = url
   req = requests.get(successor_url+"/get_song_list")
   successor_song_list = req.json()
   if str(key_identifier) in successor_song_list:
     answer = {}
     answer['value'] = successor_song_list[str(key_identifier)]
   else:
     ## Check if Node's replica_list contains this key
     req = requests.get(successor_url+"/get_replica_list")
     successor_replica_list = req.json()
     if str(key_identifier) in successor_replica_list:
       val_arr = successor_replica_list[str(key_identifier)]
       answer = {}
       answer['value'] = val_arr[0]
     else:
       ## Check if any other Node's song_list or replica_list contains this key
       successor = requests.get(url+"/get_successor")
       successor = successor.json()
       successor_url = get_url(successor)
       while not successor_url == url:
         req = requests.get(successor_url+"/get_song_list")
         successor_song_list = req.json()
         if str(key_identifier) in successor_song_list:
           answer = {}
           answer['value'] = successor_song_list[str(key_identifier)]
           break
         req = requests.get(successor_url+"/get_replica_list")
         successor_replica_list = req.json()
         if str(key_identifier) in successor_replica_list:
           val_arr = successor_replica_list[str(key_identifier)]
           answer = {}
           answer['value'] = val_arr[0]
           break
         successor = requests.get(successor_url+"/get_successor")
         successor = successor.json()
         successor_url = get_url(successor)

   if 'value' in answer:
       print("Value of key: ", answer['value'])
   else:
       print("Key not found")
   return

def main(host,port):
  global private_net
  global public_net
  private_net['host'] = host
  private_net['port'] = port
  url = "http://"+host+":"+str(port)
  #print("Node "+url+" is joining chord ")

  if private_net['host'] == public_net['host'] and str(private_net['port']) == public_net['port']:
    ## if node joining is the coordinator he chooses replica number and replication method
    #print("Choose replica number k:")
    #k = int(sys.stdin.readline().splitlines()[0])
    k = input("Choose replica number k: ")
    #print("Choose replication method ")
    #while True:
    #replication_method = (sys.stdin.readlines().splitlines()[0])
    replication_method = input("Choose replication method: ")
      #if replication_method == "linearizability" or replication_method == "eventual consistency":
        #break
      #print("invalid replication method")
    req = requests.post(url+"/set_replication_parameters",data = {'k':k,'replication_method':replication_method})

  ## Node joins Chord
  req = requests.get(url+"/join")
  print(req.text)
  req = requests.get(url+"/get_replication_parameters")
  replication_parameters = req.json()
  k = int(replication_parameters['k'])
  replication_method = replication_parameters['replication_method']

  while True:
    minput = sys.stdin.readline()
    minput = minput.splitlines()[0]
    cmd_arr = minput.split()
    cmd_arr_size = len(cmd_arr)
    if cmd_arr_size == 0:
      print("No command")
    else:

      cmd = cmd_arr[0]
      separator = " "
      key_value = separator.join(cmd_arr[1:])
      key_value_arr = key_value.split(",")
      key_value_arr_size = len(key_value_arr)

      if cmd == "insert" and key_value_arr_size == 2:

        key = key_value_arr[0]
        value = key_value_arr[1]
        hash_value = hashlib.sha1(key.encode())
        key_identifier = int(hash_value.hexdigest(),16)
        #hash_value = hashlib.sha1(value.encode())
        #value_identifier = int(hash_value.hexdigest(),16)
        value_identifier = value
        req = requests.post(url+"/"+cmd,data = {'key': key_identifier, 'value': value_identifier})
        print(req.text)
        if replication_method == "eventual consistency":
          insert_eventual_consistency(url,key_identifier,value_identifier,k)


      elif (cmd_arr[0] == "delete" or cmd_arr[0] == "query") and key_value_arr_size == 1 and not (key_value_arr[0] == ""):
        key = key_value_arr[0]
        hash_value = hashlib.sha1(key.encode())
        key_identifier = int(hash_value.hexdigest(),16)
        if cmd == "delete" or (cmd == "query" and replication_method == "linearizability") or k == 1 or key == "*":
          req = requests.post(url+"/"+cmd,data = {'key': key_identifier})
        if cmd == "query":
          if not key == "*":
            if replication_method == "eventual consistency" and k > 1:
              query_eventual_consistency(url,key_identifier)

            else:
              if 'value' in req.json():
                print("Value of key: ", req.json()['value'])
              else:
                print("Key not found")
          else:
            print(req.text)
        if cmd == 'delete':
          print(req.text)
      elif (cmd == "depart" or cmd == "overlay" or cmd == "help") and key_value_arr_size == 1 and key_value_arr[0] == "":
        req = requests.get(url+"/"+cmd)
        if cmd == "depart":
          print(req.text)
          break
        elif cmd == "overlay":
          print("Chord structure:")
        print(req.text)
        #if cmd == "overlay":
        #  print_graph(req.text)
      else:
        print(key_value_arr[0])
        print("invalid command")

if __name__ == '__main__':
  host = sys.argv[1]
  port = int(sys.argv[2])
  main(host,port)
