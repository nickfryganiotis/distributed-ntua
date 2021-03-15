from finger import Finger 
class Node:                                                                                                                                                                                          
  def __init__(self,identifier,ip,port,finger_table = [],predecessor = None,song_list = {}):
     self.identifier = identifier
     self.ip = ip
     self.port = port
     self._finger_table = finger_table
     self._predecessor = predecessor
     self._song_list = song_list
  def get_url(self):
     return "http://"+self.ip+":"+str(port)

  def get_finger_table(self):
    return self._finger_table

  def get_predecessor(self):
    return self._predecessor

  def set_predecessor(self,predecessor):
    self._predecessor = predecessor

  def set_node_to_finger_table(self,ind,n):
    self.finger[ind].set_node(n)

  def add_finger_to_finger_table(self,f):
    self._finger_table.append(f)

  def add_to_song_list(self,key,value):
    self._song_list[key] = value

  def delete_from_song_alist(self,key): 
      del self._song_list[key]                                                                                                                                                                                                                                                