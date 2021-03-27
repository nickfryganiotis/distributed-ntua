class Node:
    def __init__(self,identifier,host,port,predecessor = {}, successor = {},song_list = {},replica_list = {}):
        self.identifier = identifier
        self.host = host
        self.port = port
        self._predecessor = predecessor
        self._successor = successor
        self._song_list = song_list
        self._replica_list = replica_list

    def set_predecessor(self,predecessor):
        self._predecessor = predecessor

    def set_successor(self,successor):
        self._successor = successor

    def set_song_to_song_list(self,key,value):
        self._song_list[key] = value

    def set_replica_to_replica_list(self,key,value):
        self._replica_list[key] = value

    def get_predecessor(self):
        return self._predecessor

    def get_successor(self):
        return self._successor

    def get_song_list(self):
        return self._song_list

    def get_replica_list(self):
        return self._replica_list

    def delete_song_from_song_list(self,key):
        if key in self._song_list:
            del self._song_list[key]

    def delete_replica_from_replica_list(self,key):
        if key in self._replica_list:
            del self._replica_list[key]