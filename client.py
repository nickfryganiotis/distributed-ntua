import sys
import os
import requests
import hashlib

def main(host,port):
 url = "http://"+host+":"+str(port)
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