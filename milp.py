import gurobipy as gp
import classes
import functions
import scipy.spatial.distance as distance
from gurobipy import GRB, quicksum

def solve(instance):
    solution = classes.Solution(instance.Days)

    model = gp.Model()

    def calc_dist(list_i,list_j):
        return functions.euclidean(list_i[0],list_j[0],list_i[1],list_j[1])
    #Sets
    R = {} #requests
    K = 0 # max number of trucks required
    S = 0 #technicians
    S_0 = {} #starts with technicians locations then requests
    R_s = []
    #Params
    T = instance.Days
    H_0 = [instance.Locations.get(1)[0],instance.Locations.get(1)[1]]
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

    for technician in instance.Technicians:
        H_s.append(instance.Locations[(technician.locID)])
        D_s.append(technician.maxDistance)
        N_s.append(technician.maxInstalls)
        S+=1
        S_0[len(S_0)] = [instance.Locations[technician.locID][0],instance.Locations[technician.locID][1]]

        can_install = []
        current_tech = []
        for request in instance.Requests:
            if(request.machineID in technician.machines):
                current_tech.append(1)
                can_install.append(request.ID)
            else:
                current_tech.append(0)
        can_install.append(len(S_0)+len(instance.Requests))
        R_s.append(can_install)
        a_si.append(current_tech)

    for request in instance.Requests:
        e.append(request.firstDay)
        l.append(request.lastDay)
        c_i.append(request.size)
        idle_cost = request.amount*instance.Machines[request.machineID-1].penalty
        CI_i.append(idle_cost)
        K+=request.amount
        location = [instance.Locations.get(request.locID)[0],instance.Locations.get(request.locID)[1]]
        R[request.ID] = location
        S_0[len(S_0)] = location


    R_0 = {**{0:H_0},**R} # Requests and depot (at 0)


    #Decision variables
    #x_ij_k truck visits location j after location i: 1 if truck visits, 0 otherwise
    #LIST MET LOCATIONS NOG INVULLEN

    x = model.addVars(((t,k,i,j) for t in range(1,T+1) for k in range(K) for i in R_0 for j in R_0), vtype=GRB.BINARY, name='xij')

    z = model.addVars(((t,s,i,j) for t in range(1,T+1) for s in S_0 for i in S_0 for j in S_0), vtype=GRB.BINARY, name='zij')
    #m_k number of trucks used for entire planning: 1 if truck k is used, 0 otherwise
    m = model.addVars((k for k in range(K)), vtype=GRB.BINARY, name = 'numTrucks')

    #r_s number of technicians used for entire planning: 1 if technician is used, 0 otherwise
    r = model.addVars((s for s in range(S)), vtype=GRB.BINARY, name = 'r')

    #v_k_t truck k is used during day: 1 if used, 0 otherwise
    v = model.addVars(((t,k) for t in range(1,T+1) for k in range(K)), vtype=GRB.BINARY, name = 'v')

    #p_s_t technician s is used during day: 1 if used, 0 otherwise
    p = model.addVars(((t,s) for t in range(1,T+1) for s in range(S)), vtype=GRB.BINARY, name = 'p')

    #w_i_t request i is delivered on day: 1 if delivered, 0 otherwise
    w = model.addVars(((t,i) for t in range(1,T+1) for i in R), vtype=GRB.BINARY, name = 'w')

    #y_i_t request i is installed on day: 1 if installed, 0 otherwise
    y = model.addVars(((t,i) for t in range(1,T+1) for i in R), vtype=GRB.BINARY, name = 'y')

    #g_is number of visits done by technician
    g = model.addVars(((i, s) for s in range(S) for i in R_s[s]),vtype=GRB.INTEGER, name='g')

    #b_i number of days installation of request j is delayed after its delivery
    b = model.addVars(((i) for i in R),vtype=GRB.INTEGER, name='b')

    # 1 Objective
    
    obj = quicksum(CV*m[k] for k in range(K)) + \
        quicksum(CVU*v[t,k] for t in range(1,T+1) for k in range(K)) + \
        quicksum(CVT*calc_dist(R_0.get(i),R_0.get(j))*x[t,k,i,j] for k in range(K) for t in range(1,T+1) for i in R_0 for j in R_0 if i!=j) + \
        quicksum(CT*r[s] for s in range(S)) + \
        quicksum(CTU*p[t,s] for t in range(1,T+1) for s in range(S)) + \
        quicksum(CTT*calc_dist(S_0.get(i-1),S_0.get(j-1))*z[t,s,i-1,j-1] for s in range(S) for i in R_s[s] for j in R_s[s] if i!=j  for t in range(1,T+1)) + \
        quicksum(CI_i[i-1]*b[i] for i in R)

    # 2 arcs entering location = arcs exiting location
    model.addConstrs(quicksum(x[t,k,i,j] for j in R_0 if i!=j) == quicksum(x[t,k,j,i] for j in R_0 if i!=j) for i in R_0 for k in range(K) for t in range(1,T+1))
    # 3 start and end routes at depot
    model.addConstrs(quicksum(x[t,k,i,0] for i in R) == quicksum(x[t,k,0,i] for i in R) for k in range(K) for t in range(1,T+1))

    # 4 Max distance truck can drive
    model.addConstrs(quicksum(calc_dist(R_0.get(i),R_0.get(j))*x[t,k,i,j] for i in R_0 for j in R_0 if i!=j) <= D for k in range(K) for t in range(1,T+1))

    # 5 Truck must be available
    model.addConstrs((v[t,k] <= m[k]) for k in range(K) for t in range(1,T+1))

    # 6 Truck used for day and can travel
    model.addConstrs((x[t,k,i,j]<=v[t,k]) for i in R_0 for j in R_0 for k in range(K) for t in range(1,T+1))

    # 7 Delivery timewindow
    model.addConstrs((quicksum(x[t,k,i-1,j] for k in range(K) for j in R_0 if i-1!=j))==(w[t,i]) for i in R for t in range(e[i-1],l[i-1]+1))

    # 8 Each request is delivered
    model.addConstrs(quicksum(w[t,i] for t in range(e[i-1],l[i-1]) ) == 1 for i in R)

    # 9 --
    # 10 --
    # 11 A location should be visited by technician
    model.addConstrs(quicksum(z[t,s,i-1,j-1] for j in R_s[s] if i!=j) == quicksum(z[t,s,j-1,i-1] for j in R_s[s] if i!=j) for s in range(S) for i in R_s[s]  for t in range(1,T+1))

    # 12 start and end route at depot
    model.addConstrs(quicksum(z[t,s,i,s+len(R)] for i in R) == quicksum(z[t,s,s+len(R),i] for i in R) for s in range(S) for t in range(1,T+1))

    # 13 Technician max distance
    model.addConstrs(quicksum(calc_dist(S_0.get(i-1),S_0.get(j-1))*z[t,s,i-1,j-1] for i in R_s[s] for j in R_s[s] if i!=j)<=D_s[s] for t in range(1,T+1) for s in range(S))

    # 14 Max number of installs
    model.addConstrs(quicksum(z[t,s,i-1,j] for i in R_s[s] for j in R if i!=j)<=N_s[s] for t in range(1,T+1) for s in range(S))

    # 15 Technician has been hired
    model.addConstrs(p[t,s]<=r[s] for t in range(1,T+1) for s in range(S))

    # 16 Technician can travel between requests in one day
    model.addConstrs(z[t,s,i-1,j-1]<=p[t,s] for t in range(1,T+1) for s in range(S) for i in R_s[s] for j in R_s[s])

    # 17 Machine can be installed one day after delivery
    model.addConstrs(quicksum(z[t,s,i-1,j-1] for s in range(S) for j in R_s[s] if i!=j)==y[t,i] for i in R for t in range(1+e[i-1],T+1))

    # 18 Each request is installed
    model.addConstrs(quicksum(y[t,i] for t in range(e[i-1]+1,T+1) ) == 1 for i in R)

    # 19 subtours never form in technician routes.
    model.addConstrs(g[j,s] <= g[i,s]-(z[t,s,i-1,j-1])*(1+N_s[s])+N_s[s] for s in range(S) for i in R_s[s] for j in R if i!=j for t in range(1,T+1))

    # 20 Max number of visits technician per day
    model.addConstrs(g[s+1+len(R),s]==N_s[s] for s in range(S))

    # 21 Technician can work  4 consecutive days but rest 1 day
    model.addConstrs(quicksum(p[u,s] for u in range(t+1,t+4+1)) <=5-p[t+5,s] for s in range(S) for t in range(1,T+1-5))

    # 22 Technician can work 5 consecutive days but rest 2 days
    model.addConstrs(quicksum(p[u,s] for u in range(t+1,t+4+1)) <=5-p[t+6,s] for s in range(S) for t in range(1,T+1-6))

    # 23 Prevents technicians from working more than 5 days in the last 6 days
    model.addConstrs(quicksum(p[u,s] for u in range(T+1-5,T)) <=5-p[T,s] for s in range(S))

    # 24 

    model.setObjective(obj,GRB.MINIMIZE)

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

    
