import gurobipy as gp
import classes
import functions
import scipy.spatial.distance as distance

def solve(instance):
    solution = classes.Solution(instance.Days)

    model = gp.Model()

    trucks = [] # max number of trucks required

    #Sets
    R = instance.Requests
    
    #Params
    T = instance.Days
    H_0 = instance.Locations.get(1)
    print(type(R))
    R_0 = [list(H_0)] + R # Requests and home depot
    D = instance.TruckMaxDistance
    #M_t = instance ?? Mt: upper bound on the number of visits a vehicle can do to depot on day t.
    coordinates = list(instance.Locations.values())
    #dist between locations 1 and 2 with d_ij[0][1]
    d_ij = distance.cdist(coordinates,coordinates,'euclidean')
    e = [] # first day that request i can be delivered
    l = [] # last day that request i can be delivered
    C = instance.TruckCapacity #Truck capacity
    c_i = [] #capacity needed to deliver request i
    a_si =[] #1 if tech s can satisfy request i
    H_s = [] #Home location of technician
    D_s = [] #max distance that technician s can travel per day
    N_s = [] #max number of installs tech s can do per day
    CI_i = [] #cost of delaying the installation of request i per day
    CV = instance.TruckCost
    CT = instance.TechnicianCost
    CVU = instance.TruckDayCost
    CTU = instance.TechnicianDayCost
    CVT = instance.TruckDistanceCost
    CTT = instance.TechnicianDistanceCost

    for request in instance.Requests:
        e.append(request.firstDay)
        l.append(request.lastDay)
        c_i.append(request.size)
        idle_cost = request.amount*instance.Machines[request.machineID-1].penalty
        CI_i.append(idle_cost)

    for technician in instance.Technicians:
        current_tech = []
        for request in instance.Requests:
            if(request.machineID in technician.machines):
                current_tech.append(1)
            else:
                current_tech.append(0)
        a_si.append(current_tech)
        H_s.append(instance.Locations[(technician.locID)])
        D_s.append(technician.maxDistance)
        N_s.append(technician.maxInstalls)
    

    #Decision variables
    #model.addVar(for day in instance.Days for k in trucks for )