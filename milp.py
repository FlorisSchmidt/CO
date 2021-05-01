import gurobipy as gp
import classes
import functions
import scipy.spatial.distance as distance
from gurobipy import GRB, quicksum

def solve(instance):
    solution = classes.Solution(instance.Days)

    model = gp.Model()

    #Sets
    R = instance.Requests #requests
    K = 0 # max number of trucks required
    S = 0 #technicians
    R_s = []
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
    a_si =[] #1 if technician s can satisfy request i
    H_s = [] #Home location of technician
    D_s = [] #max distance that technician s can travel per day
    N_s = [] #max number of installs technician s can do per day
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
        K+=request.amount

    for technician in instance.Technicians:
        current_tech = []
        can_install = [instance.Locations[(technician.locID)]]
        for request in instance.Requests:
            if(request.machineID in technician.machines):
                current_tech.append(1)
                can_install.append(request.ID)
            else:
                current_tech.append(0)
        
        R_s.append(can_install)
        a_si.append(current_tech)
        H_s.append(instance.Locations[(technician.locID)])
        D_s.append(technician.maxDistance)
        N_s.append(technician.maxInstalls)
        S+=1

    #Decision variables
    #x_ij_k truck visits location j after location i: 1 if truck visits, 0 otherwise
    #LIST MET LOCATIONS NOG INVULLEN

    x = model.addVars(((t,k,i,j) for t in range(T) for k in range(K) for i in R for j in R), vtype=GRB.BINARY, name='xij')

    z = model.addVars(((t,s,i,j) for t in range(T) for s in range(S) for i in R for j in R), vtype=GRB.BINARY, name='zij')
    #m_k number of trucks used for entire planning: 1 if truck k is used, 0 otherwise
    m = model.addVars((k for k in range(K)), vtype=GRB.BINARY, name = 'numTrucks')

    #r_s number of technicians used for entire planning: 1 if technician is used, 0 otherwise
    r = model.addVars((s for s in range(S)), vtype=GRB.BINARY, name = 'r')

    #v_k_t truck k is used during day: 1 if used, 0 otherwise
    v = model.addVars(((t,k) for t in range(T) for k in range(K)), vtype=GRB.BINARY, name = 'v')

    #p_s_t technician s is used during day: 1 if used, 0 otherwise
    p = model.addVars(((t,s) for t in range(T) for s in range(S)), vtype=GRB.BINARY, name = 'p')

    #w_i_t request i is delivered on day: 1 if delivered, 0 otherwise
    w = model.addVars(((t,i) for t in range(T) for i in R), vtype=GRB.BINARY, name = 'w')

    #y_i_t request i is installed on day: 1 if installed, 0 otherwise
    y = model.addVars(((t,i) for t in range(T) for i in R), vtype=GRB.BINARY, name = 'y')

    #g_is number of visits done by technician
    g = model.addVars(((s, i) for s in range(S) for i in R),vtype=GRB.INTEGER, name='g')

    #b_i number of days installation of request j is delayed after its delivery
    b = model.addVars(((i) for i in R),vtype=GRB.INTEGER, name='b')

    #Objective
    model.setObjective(quicksum(m),GRB.MINIMIZE)

    #arcs entering location = arcs exiting location
    model.addConstrs((x[t,k,i,j] == x[t,k,j,i] for i,j in R_0 if i!=j) for t in range(T) for k in range(K))
    #start and end routes at depot
    model.addConstrs((x[t,k,H_0,i] == x[t,k,i,H_0] for i in R) <= v[t,k] for k in range(K) for t in range(T))
    #Max distance truck can drive
    model.addConstrs(quicksum(d_ij[i][j]*x[t,k,i,j] for i,j in R_0 if i!=j) <= D for t in range(T) for k in range(K))
    #Truck must be available
    model.addConstrs((v[t,k] <= m[k]) for k in range(K) for t in range(T))


    model.Params.LogToConsole = True
    model.optimize()
    model.update()
    print("End")
    #def cost():
    #    quicksum(CV*m)# + quicksum(CV*i for i in v) + quicksum(quicksum())

    #Constraints
    #max distance truck constraint
    #model.addConstr((quicksum(d_ij[i][j]*x[i,j,k] for i,j in coordinates) <= D for k in trucks), name='maxTruckDistance')

    #ensures that no more trucks can be used on a day than the number of trucks for the entire planning
    #model.addConstr((v[day,k] for day in instance.Days <= m[k] for k in trucks), name='noMoreThanMaxTrucksOnADay')

    
