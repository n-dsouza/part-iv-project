from __future__ import division
from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import json
import urllib

def create_data_model():
	"""Stores the data for the problem."""
	data = {}
	data['API_key'] = 'AIzaSyAJNMb6TPHQ1ZrYtwqG1953e-y1c1dFt7w'

	data['hardcode'] = 0

	# Hardcode distance matrix if needed
	if (data['hardcode']):
		print()
		print('hardcode')
		data['distance_matrix'] = [
			# Weird. Some numbers in this matrix were wrong. How come?!
			# [0, 283, 16261, 3063, 10244],
			# [267, 0, 16186, 2823, 10004],
			# [13037, 13057, 0, 11578, 16300],
			# [3034, 2796, 12876, 0, 7602],
			# [10394, 10156, 17244, 7718, 0]
			[0, 283, 15485, 3063, 10254],
			[267, 0, 15410, 2823, 10014],
			[13037, 13057, 0, 11578, 17387],
			[3034, 2796, 12100, 0, 7611],
			[10411, 10173, 16484, 7735, 0]

		] # yapf: disable
	else:
		print()
		print('-----------------------------------------------------------------------------------------------------------------------------')
		print('NOT hardcode')
		data['addresses'] = ['21/19+Donovan+St+Blockhouse+Bay+Auckland', # depot
			'3/7+Heaphy+St+Blockhouse+Bay+Auckland',
			'Queen+Street+Auckland',
			'New+Lynn+Auckland',
			'Henderson+Auckland'
		]
		print()
		for row in data['addresses']:
			print(row)
	print()

	data['num_vehicles'] = 1
	data['depot'] = 0
	return data

def create_distance_matrix(data):
	if(data['hardcode']):
		return data['distance_matrix']
	else:
		addresses = data["addresses"]
		API_key = data["API_key"]
		# Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
		max_elements = 100
		num_addresses = len(addresses) # 16 in this example.
		# Maximum number of rows that can be computed per request (6 in this example).
		max_rows = max_elements // num_addresses
  		# num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
		q, r = divmod(num_addresses, max_rows)
		dest_addresses = addresses
		distance_matrix = []
  		# Send q requests, returning max_rows rows per request.
		for i in range(q):
			origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
			response = send_request(origin_addresses, dest_addresses, API_key) # Create URL
			distance_matrix += build_distance_matrix(response) # List Concatenation
			
		# Get the remaining remaining r rows, if necessary.
		if r > 0:
			origin_addresses = addresses[q * max_rows: q * max_rows + r]
			response = send_request(origin_addresses, dest_addresses, API_key)
			distance_matrix += build_distance_matrix(response)
	for row in distance_matrix:
		print(row)
	return distance_matrix

def send_request(origin_addresses, dest_addresses, API_key):
	### Build and send request for the given origin and destination addresses.
	### This function creates a URL to access the json file through the API. and grab distance.
	def build_address_str(addresses):
		# Build a pipe-separated string of addresses
		address_str = ''
		for i in range(len(addresses) - 1):
			address_str += addresses[i] + '|'
			address_str += addresses[-1]
		return address_str
	
	request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric'
	origin_address_str = build_address_str(origin_addresses) # Same number of addresses as Max Rows
	dest_address_str = build_address_str(dest_addresses) # All destination addresses
	request = request + '&origins=' + origin_address_str + '&destinations=' + \
					   dest_address_str + '&key=' + API_key
	jsonResult = urllib.request.urlopen(request).read()
	response = json.loads(jsonResult)
	return response

def build_distance_matrix(response):
	### List concatenation happens in this function
  distance_matrix = []
  for row in response['rows']:
	  row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
	  distance_matrix.append(row_list)
  return distance_matrix
''' 

Tomorrow's tasks:
1. Create a 'var' data structure or something. Something that can be input directly into HTML (Proof of concept. Later Leaflet or whatever)
2. Put the Distance Matrix code in same place as the TSP code.
3. Figure a way to call/interface with HTML from python and vice versa (maybe just writing to file?)
4. Figure a way to load a map on browser (html, open! from python)
5. Figure a way to draw lines
6. Basically, while you're doing all the plotting as above, see if there is a way to plot from ortools directly!
7. Web scraping for Countdown locations! Plot em.
8. See if there's a way to click on HTML map and store the clicks. That database of lng/lat convert to address.
9. This code did address to API distance matrix. 
  9.1 Is there a way to do Address to Lat/Lng to plot on HTML map?
  9.2 What about plotting straight Address on HTML map?
  9.3 What about using lat/lng as the input for distance matrix (currently it's addresses (english) see above in this file!)
  
'''

# https://developers.google.com/optimization/routing/tsp
###########################################################
"""Simple travelling salesman problem between cities."""
###########################################################

def print_solution(manager, routing, assignment):
	"""Prints assignment on console."""
	print('Objective: {} miles'.format(assignment.ObjectiveValue()))
	index = routing.Start(0)
	plan_output = 'Route for vehicle 0:\n'
	route_distance = 0
	while not routing.IsEnd(index):
		plan_output += ' {} ->'.format(manager.IndexToNode(index))
		previous_index = index
		index = assignment.Value(routing.NextVar(index))
		route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
	plan_output += ' {}\n'.format(manager.IndexToNode(index))
	print(plan_output)
	plan_output += 'Route distance: {}miles\n'.format(route_distance)


def main():
	"""Entry point of the program."""
	# Instantiate the data problem.
	# data = create_data_model()
	data = create_data_model()

	# addresses = data['addresses']
	# API_key = data['API_key']
	data['distance_matrix'] = create_distance_matrix(data)
	# for row in data['distance_matrix']:
	# 	print(row)

	# Create the routing index manager.
	manager = pywrapcp.RoutingIndexManager(
		len(data['distance_matrix']), data['num_vehicles'], data['depot'])

	# Create Routing Model.
	routing = pywrapcp.RoutingModel(manager)


	def distance_callback(from_index, to_index):
		"""Returns the distance between the two nodes."""
		# Convert from routing variable Index to distance matrix NodeIndex.
		from_node = manager.IndexToNode(from_index)
		to_node = manager.IndexToNode(to_index)
		return data['distance_matrix'][from_node][to_node]

	transit_callback_index = routing.RegisterTransitCallback(distance_callback)

	# Define cost of each arc.
	routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

	# Setting first solution heuristic.
	search_parameters = pywrapcp.DefaultRoutingSearchParameters()
	search_parameters.first_solution_strategy = (
		routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

	# Solve the problem.
	assignment = routing.SolveWithParameters(search_parameters)

	# Print solution on console.
	if assignment:
		print_solution(manager, routing, assignment)


if __name__ == '__main__':
	main()
	print('--------------------------------------------------------------')