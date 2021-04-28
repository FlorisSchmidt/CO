import gurobipy as gp
import classes
import functions
import scipy

def solve(instance):
    solution = classes.Solution(instance.Days)

    model = gp.Model()

    trucks = []

    #Sets
    R = instance.Requests
    R_0 = 

    #Params
    T = instance.Days
    H_0 = instance.Locations.get(1)
    D = instance.TruckMaxDistance
    #M_t = instance ?? Mt: upper bound on the number of visits a vehicle can do to depot on day t.
    coordinates = list(instance.Locations.values())
    #dist between locations 1 and 2 with d_ij[0][1]
    d_ij = scipy.spatial.distance.cdist(coordinates,coordinates,'euclidean')
    e = []
    l = []
    C = instance.TruckCapacity
    c 
    for request in instance.Requests:
        request.id
        request.firstDay
