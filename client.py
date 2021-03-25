import sys
import os
import requests
import hashlib


public_net = {}
public_net['host'] = "192.168.0.1"
public_net['port'] = "5000"
private_net = {}

def main(host,port):
  global private_net
  global public_net
  private_net['host'] = host
  private_net['port'] = port
  url = "http://"+host+":"+str(port)
  print("Node "+url+" is joining chord ")
  
  if private_net['host'] == public_net['host'] and private_net['port'] == public_net['port']:
    ## if node joining is the coordinator he chooses replica number and replication method
    print("Choose replica number k:")
    k = int(sys.stdin.readline().splitlines()[0])
    print("Choose replication method ")
    while True:
      replication_method = (sys.stdin.readlines().splitlines()[0])
      if replication_method == "linearizability" or replication_method == "eventual consistency":
        break
      print("invalid replication method")  
    req = requests.post(url+"/set_replication_parameters",data = {'k':k,'replication_method':replication_method})
  
  ## Node joins dht
  req = requests.get(url+"/join")

  while True:
    input = sys.stdin.readline()
    input = input.splitlines()[0]
    cmd_arr = input.split()
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
        hash_value = hashlib.sha1(value.encode())
        value_identifier = int(hash_value.hexdigest(),16)
        req = requests.post(url+"/"+cmd,data = {'key': key_identifier, 'value': value_identifier})
      elif (cmd_arr[0] == "delete" or cmd_arr[0] == "query") and key_value_arr_size == 1 and not (key_value_arr[0] == ""):
        key = key_value_arr[0]
        hash_value = hashlib.sha1(key.encode())
        key_identifier = int(hash_value.hexdigest(),16)
        req = requests.post(url+"/"+cmd,data = {'key': key_identifier})
        if cmd == "query":
          if not key == "*":
            print(req.json())
          else:
            print(req.text)

      elif (cmd == "depart" or cmd == "overlay" or cmd == "help") and key_value_arr_size == 1 and key_value_arr[0] == "":
        req = requests.get(url+"/"+cmd)
        if cmd == "depart":
          break
        print(req.text)
      else:
        print(key_value_arr[0])
        print("invalid command")
if __name__ == '__main__':
  host = sys.argv[1]
  port = int(sys.argv[2])
  main(host,port)