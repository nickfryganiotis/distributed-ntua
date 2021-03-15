import sys
import requests
import hashlib
#req = requests.get("http://192.168.0.1:5000/join")
def main(host,port):
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
        identifier = int(hash_value.hexdigest(),16)
        print(cmd)
        print(identifier)
      elif (cmd_arr[0] == "delete" or cmd_arr[0] == "query") and key_value_arr_size == 1 and not (key_value_arr[0] == ""):
        key = key_value_arr[0]
        hash_value = hashlib.sha1(key.encode())
        identifier = int(hash_value.hexdigest(),16)
        print(cmd)
        print(identifier)
      elif (cmd == "depart" or cmd == "overlay" or cmd == "help") and key_value_arr_size == 1 and key_value_arr[0] == "":
        if cmd == "depart":
          break
        print(cmd)
      else:
        print(key_value_arr[0])
        print("invalid command")
if __name__ == '__main__':
  host = sys.argv[1]
  port = int(sys.argv[2])
  main(host,port)