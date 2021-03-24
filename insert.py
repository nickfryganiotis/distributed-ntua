import requests
import random
import hashlib
import time

def main():
    url = []
    url.append("192.168.0.1:5000/insert")
    url.append("192.168.0.1:5001/insert")
    url.append("192.168.0.2:5000/insert")
    url.append("192.168.0.2:5001/insert")
    url.append("192.168.0.3:5000/insert")
    url.append("192.168.0.3:5001/insert")
    url.append("192.168.0.4:5000/insert")
    url.append("192.168.0.4:5001/insert")
    url.append("192.168.0.5:5000/insert")
    url.append("192.168.0.5:5001/insert")
    f = open("insert.txt")
    lines = f.readlines()
    start_time = time.time()
    for line in lines:
        args = line.split(',')
        random_node = random.randint(0,9)
        key = args[0]
        value = args[1].splitlines()[0]
        hash_value = hashlib.sha1(key.encode())
        key_identifier = int(hash_value.hexdigest(),16)
        hash_value = hashlib.sha1(value.encode())
        value_identifier = int(hash_value.hexdigest(),16)
        req = requests.post(url[random_node],data = {'key': key_identifier, 'value': value_identifier})
    print(time.time() - start_time)
    f.close()


if __name__ == '__main__':
    main()