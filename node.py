from finger import Finger
class Node:
  def __init__(self,identifier,host,port,finger_table = [],predecessor = {},song_list = {}):
     self.identifier = identifier
     self.host = host
     self.port = port
     self._finger_table = finger_table
     self._predecessor = predecessor
     self._song_list = song_list
  def get_url(self):
     return "http://"+self.host+":"+str(port)

  def get_finger_table(self):
    return self._finger_table

  def get_predecessor(self):
    return self._predecessor

  def set_predecessor(self,predecessor_host,predecessor_port):
    self._predecessor['host'] = predecessor_host
    self._predecessor['port'] = predecessor_port

  def set_node_to_finger_table(self,ind,node_host,node_port):
    self._finger_table[ind].set_node(node_host,node_port)

  def add_finger_to_finger_table(self,f):
    self._finger_table.append(f)

  def add_to_song_list(self,key,value):
    self._song_list[key] = value

  def delete_from_song_alist(self,key):
    del self._song_list[key]