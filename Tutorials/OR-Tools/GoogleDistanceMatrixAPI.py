from __future__ import division
from __future__ import print_function
import requests
import json
import urllib


def create_data():
  ### Creates the data.
  data = {}
  data['API_key'] = 'AIzaSyAJNMb6TPHQ1ZrYtwqG1953e-y1c1dFt7w'
  #data['addresses'] = ['3610+Hacks+Cross+Rd+Memphis+TN', # depot
                    #    '1921+Elvis+Presley+Blvd+Memphis+TN',
                    #    '149+Union+Avenue+Memphis+TN',
                    #    '1034+Audubon+Drive+Memphis+TN',
                    #    '1532+Madison+Ave+Memphis+TN',
                    #    '706+Union+Ave+Memphis+TN',
                    #    '3641+Central+Ave+Memphis+TN',
                    #    '926+E+McLemore+Ave+Memphis+TN',
                    #    '4339+Park+Ave+Memphis+TN',
                    #    '600+Goodwyn+St+Memphis+TN',
                    #    '2000+North+Pkwy+Memphis+TN',
                    #    '262+Danny+Thomas+Pl+Memphis+TN',
                    #    '125+N+Front+St+Memphis+TN',
                    #    '5959+Park+Ave+Memphis+TN',
                    #    '814+Scott+St+Memphis+TN',
                    #    '1005+Tillman+St+Memphis+TN'
                    #   ]

  data['addresses'] = ['21/19+Donovan+St+Blockhouse+Bay+Auckland', # depot
                       '3/7+Heaphy+St+Blockhouse+Bay+Auckland',
                       'Queen+Street+Auckland',
                       'New+Lynn+Auckland',
                       'Henderson+Auckland'
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    '',
                    #    ''
                      ]

  return data

def create_distance_matrix(data):
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

########
# Main #
########
def main():
  ### Entry point of the program
  # Create the data.
  data = create_data()
  addresses = data['addresses']
  API_key = data['API_key']
  distance_matrix = create_distance_matrix(data)
  for row in distance_matrix:
	  print(row)


if __name__ == '__main__':
  main()

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