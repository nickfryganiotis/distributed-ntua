class Node:
    def __init__(self,identifier,host,port,predecessor = {}, successor = {},song_list = {}):
        self.identifier = identifier
        self.host = host
        self.port = port
        self._predecessor = predecessor
        self._successor = successor
        self._song_list = song_list
    
    def set_predecessor(self,predecessor):
        self._predecessor = predecessor
    
    def set_successor(self,successor):
        self._successor = successor
    
    def set_song_to_song_list(self,key,value):
        self._song_list[key] = value
    
    def get_predecessor(self):
        return self._predecessor
    
    def get_successor(self):
        return self._successor
    
    def get_song_list(self):
        return self._song_list
    
    def delete_song_from_song_list(self,key):
        del self._song_list[key]
        