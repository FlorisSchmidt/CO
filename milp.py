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
    #x_ij_k truck visits location j after location i: 1 if truck visits, 0 otherwise
    #LIST MET LOCATIONS NOG INVULLEN
    x = model.addVar((), vtype=GRB.BINARY, name='xij')

    #m_k number of trucks used for entire planning: 1 if truck k is used, 0 otherwise
    m = model.addVar((k for k in trucks), ub=D , vtype=GRB.BINARY, name = 'numTrucks')

    #r_s number of technicians used for entire planning: 1 if technician is used, 0 otherwise
    r = model.addVar((s for s in instance.Technicians), vtype=GRB.BINARY, name = 'r')

    #v_k_t truck k is used during day: 1 if used, 0 otherwise
    v = model.addVar(((day,k) for day in instance.Days for k in trucks), vtype=GRB.BINARY, name = 'vkt')

    #p_s_t technician s is used during day: 1 if used, 0 otherwise
    p = model.addVar(((day,s) for day in instance.Days for s in instance.Technicians), vtype=GRB.BINARY, name = 'pst')

    #w_i_t request i is delivered on day: 1 if delivered, 0 otherwise
    w = model.addVar(((day,t) for day in instance.Days for t in request), vtype=GRB.BINARY, name = 'wit')

    #y_i_t request i is installed on day: 1 if installed, 0 otherwise
    #y = model.addVar(((day,i) for day in instance.Days for i in instance.installation), vtype=GRB.BINARY, name = 'yit')

    #g_is number of visits done by technician
    #g = model.addVar((route, request) for route in SolutionDay.TechnicianRoute for request in SolutionDay.TechnicianRequests,vtype=GRB.INTEGER, name='gis')

    #b_i number of days installation of request j is delayed after its delivery

    #Constraints
    #max distance truck constraint
    model.addConstr((gp.quicksum(d_ij[i][j]*x[i,j,k] for i,j in coordinates) <= D for k in trucks), name='maxTruckDistance')

    #ensures that no more trucks can be used on a day than the number of trucks for the entire planning
    model.addConstr((v[day,k] for day in instance.Days <= m[k] for k in trucks), name='noMoreThanMaxTrucksOnADay')

    
