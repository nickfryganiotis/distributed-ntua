class Finger:
  def __init__(self,identifier,index,nd = None):
      self.identifier = identifier
      self.index = index
      self._node = nd

  def start(self):
      return (self.identifier+2**self.index) % 2**160

  def set_node(self,n):
      self._node = n

  def get_node(self):
      return self._node