'''
	If the world ends because of this script, the culprit is - 
		Priyansh (pc.priyansh@gmail.com)

	This code is responsible for finding a localsubgraph for every important DBpedia entry (based on pagerank) and using it to fill the templates found in templates.py file	
'''

import matplotlib.pyplot as plt
import networkx as nx
				
def insert(G, data):
	#data - list of three tuple [(name,uri),(name,uri),(name,uri)] , data[1] - edge and data[0],data[2] is nodes
	#G is the graph object
	node1 = ""
	node2 = ""

	for node in G.node:
		if data[0][1] == node.getUri():
			node1 = node
		if data[2][1] == node.getUri():
			node2 = node
	if not node1:
		node1 = Node(data[0][0],data[0][1])
		G.add_node(node1)
	if not node2 :
		node2 = Node(data[2][0],data[2][1])
		G.add_node(node2)
	edge = Edge(data[1][0],data[1][1])
	G.add_edge(node1,node2,object=edge)

class Node():
	def __init__(self,name,uri):
		self.name = name
		self.uri = uri
	def getName(self):
		return self.name
	def getUri(self):
		return self.uri				

class Edge():
	def __init__(self,name,uri):
		self.name = name
		self.uri = uri
	def getName(self):
		return self.name
	def getUri(self):
		return self.uri

class accessGraph():
	def __init__(self,G):
		#expects a graph object
		self.G = G
	def return_node(self,node_name="",node_uri=""):
		#returns a list of node with a given name
		node_list = []
		for node in self.G.node:
			if (node.getName() == node_name or node.getUri() == node_uri):
				node_list.append(node)
		return node_list

	def return_outnodes(self,node_name):
		#note that the node_name is not unique and hence for a given node_name there would be a list of nodess and thus a list of list of nopdes would be output 
		node_list = self.return_node(node_name = node_name)
		outnodes_list = []
		for node in node_list:
			#temp will have the following structure --> ('Gaurav', 'books', {'object': 'likes'}), ('Gaurav', 'Pizza', {'object': 'loves'})]
			temp = self.G.out_edges(node)
			outnodes_list.append(temp)
		return outnodes_list
	
	def return_innodes(self,node_name):
		node_list = self.return_node(node_name)
		innodes_list = []
		for node in node_list:
			#temp will have the following structure --> ('Gaurav', 'books', {'object': 'likes'}), ('Gaurav', 'Pizza', {'object': 'loves'})]
			temp = self.G.in_edges(node)
			innodes_list.append(temp)
		return innodes_list

def draw_graph(G):
	print "trying to print"
	for node in G.node:
		print node.getName()
	print "completed printing"
	nx.draw(G)
	plt.show()


if __name__ == "__main__":
	dbp =  db_interface.DBPedia(_verbose = True)
	uri = 'http://dbpedia.org/resource/New_Delhi'
	G=nx.DiGraph()
	subgraph = get_local_subgraph(uri)
	pprint(subgraph)
	while True:
		print raw_input()	
	# fill_templates(subgraph)

	# for entity in relevent_entities: