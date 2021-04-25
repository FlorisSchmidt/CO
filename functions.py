import math

# return euclidan distance
def euclidean(xa,ya,xb,yb):
    return math.sqrt(math.pow((xa-xb),2) + math.pow((ya-yb),2))

# Insert new location in route. e.g. [1,2,1] -> [1,2,3,1]
def insert_in_route(location,route):
    old_route = route
    if not route:
        old_route += [1,location,1]
    else:
        old_route.insert(-1,location)
    return old_route

# Convert a route list eg. [0,1,2,0] to a list of coordinates eg. [[0,0],[120,120],[320,456],[0,0]]
def route_to_coordinates(routelist, locdict):
    coordinate_list = []
    for loc in routelist:
        coordinate_list.append([locdict.get(loc)[0], locdict.get(loc)[1]])
    return coordinate_list

# Calculate distance needed to travel route
def calc_route_distance(routelist, locdict):
    #print(routelist)
    coordinate_list = route_to_coordinates(routelist, locdict)
    #print(coordinate_list)
    distance = 0
    for i in range(len(coordinate_list)-1):
        distance += euclidean(coordinate_list[i][0], coordinate_list[i][1],coordinate_list[i+1][0], coordinate_list[i+1][1])
    #print(distance)
    return distance

def get_used_capacity(truck, instance):
    cap = 0
    for request in truck.requests:
        cap += instance.Machines[request.machineID - 1].size * request.amount
    return cap