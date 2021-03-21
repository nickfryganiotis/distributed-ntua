class Finger:
  def __init__(self,identifier,index,node_url = {}):
      self.identifier = identifier
      self.index = index
      self._node_url = node_url

  def start(self):
      return (self.identifier+2**self.index) % 2**160

  def set_node(self,node_host,node_port):
      self._node_url['host'] = node_host
      self._node_url['port'] = node_port

  def get_node(self):
      return self._node_url