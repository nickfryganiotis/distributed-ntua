class Node:
    def __init__(self,identifier,host,port,predecessor = {}, successor = {}):
        self.identifier = identifier
        self.host = host
        self.port = port
        self._predecessor = predecessor
        self._successor = successor
    
    def set_predecessor(self,predecessor):
        self._predecessor = predecessor
    
    def set_successor(self,successor):
        self._successor = successor
    
    def get_predecessor(self):
        return self._predecessor
    def get_successor(self):
        return self._successor
        