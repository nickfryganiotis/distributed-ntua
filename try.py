@app.route('/insert',methods = ['POST'])
def insert():
  global n
  global private_net
  global k
  results = request.form.to_dict()
  key = int(results['key'])
  value = int(results['value'])
  url = get_url(private_net)
  req = requests.post(url+"/find_successor",data = {'id': key})
  id_successor = req.json()
  primary_node = id_successor
  successor_url = get_url(id_successor)
  req = requests.post(successor_url+"/add_songs_to_song_list", data = {key:value})
  for i in range(1,k):
      req = requests.get(successor_url+"/get_successor")
      id_successor = req.json()
      if id_successor == primary_node:
        break
      successor_url = get_url(id_successor)
      req = requests.post(successor_url + "/add_replica_to_replica_list", data={key:value, 'k' : i})

  return "Insert done"


@app.route('/delete',methods = ['POST'])
def delete():
  global n
  global private_net
  results = request.form.to_dict()
  key = int(results['key'])
  url = get_url(private_net)
  req = requests.post(url+"/find_successor",data = {'id': key})
  id_successor = req.json()
  primary_node = id_sucessor
  successor_url = get_url(id_successor)
  req = requests.post(successor_url+"/delete_songs_from_song_list",data = {key: ''})
  for i in range(1,k):
      req = requests.get(successor_url+"/get_successor")
      id_successor = req.json()
      successor_url = get_url(id_successor)
      req = requests.post(successor_url + "/delete_replica_from_replica_list", data={key:value, 'k' : i})
  return "Delete done"