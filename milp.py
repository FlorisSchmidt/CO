import gurobipy as gp
import classes
import functions
import scipy.spatial.distance as distance
import pandas as pd
import copy
import output
from gurobipy import GRB, quicksum

def solve(instance, max_seconds):
    model = gp.Model()

    def calc_dist(a,b):
        return functions.euclidean(a[0],a[1],b[0],b[1])
    #Sets
    R = {} #requests
    R_0 = {} #requests and depot
    S = 0 #technicians
    R_s = {} #Technicians and able requests
    #Params
    T = instance.Days
    H_0 = [instance.Locations.get(1)[0],instance.Locations.get(1)[1]]
    D = instance.TruckMaxDistance
    truckRange = range(1,T)
    techRange = range(2,T+1)
    M = {new_list: 0 for new_list in truckRange}
    e = {} # first day that request i can be delivered
    e['depot'] = 1 # depot can always be visited
    l = {} # last day that request i can be delivered
    l['depot'] = T+1#depot can be visited on last day
    C = instance.TruckCapacity #Truck capacity
    c_i = {} #capacity needed to deliver request i
    a_si =[] #1 if technician s can satisfy request i
    H_s = [] #Home location of technician
    D_s = {} #max distance that technician s can travel per day
    N_s = {} #max number of installs technician s can do per day
    CI_i = {} #cost of delaying the installation of request i per day
    CV = instance.TruckCost
    CT = instance.TechnicianCost
    CVU = instance.TruckDayCost
    CTU = instance.TechnicianDayCost
    CVT = instance.TruckDistanceCost
    CTT = instance.TechnicianDistanceCost

    for request in instance.Requests:
        e["R"+str(request.ID)] = request.firstDay
        l["R"+str(request.ID)] = request.lastDay
        c_i["R"+str(request.ID)] = request.size
        idle_cost = request.amount*instance.Machines[request.machineID-1].penalty
        CI_i["R"+str(request.ID)] = idle_cost
        location = [instance.Locations.get(request.locID)[0],instance.Locations.get(request.locID)[1]]
        R["R"+str(request.ID)] = location
        for day in truckRange:
            if(day>=request.firstDay and day<=request.lastDay):
                M[day]+=1
    R_0 = copy.deepcopy(R)

    for technician in instance.Technicians:
        H_s.append(instance.Locations[(technician.locID)])
        D_s["S"+str(technician.ID)] = technician.maxDistance
        N_s["S"+str(technician.ID)] = technician.maxInstalls
        S+=1
        techLoc = [instance.Locations[technician.locID][0],instance.Locations[technician.locID][1]]
        can_install = {}
        current_tech = []
        for request in instance.Requests:
            if(request.machineID in technician.machines):
                current_tech.append(1)
                can_install["R"+str(request.ID)] = [instance.Locations.get(request.locID)[0],instance.Locations.get(request.locID)[1]]
            else:
                current_tech.append(0)
        can_install["S"+str(technician.ID)] = techLoc
        R_s["S"+str(S)] = can_install
        e['S'+str(S)] = 1
        a_si.append(current_tech)
    
    R_0['depot'] = H_0
    K = max(M.values())
    #Decision variables
    #x_ij_k truck visits location j after location i: 1 if truck visits, 0 otherwise
    x = model.addVars(((t,k,i,j) for t in truckRange for k in range(K) for i in R_0 if t<=l[i] and t>=e[i] for j in R_0 if i!=j and t<=l[j] and t>=e[j]), vtype=GRB.BINARY, name='x')

    #z_ij_s technician s visits location j after location i: 1 if technician visits, 0 otherwise
    z = model.addVars(((t,s,i,j) for t in techRange for s in R_s for i in R_s[s] if t>=e[i]+1 for j in R_s[s] if t>=e[j]+1 if i!=j), vtype=GRB.BINARY, name='z')

    #m_k number of trucks used for entire planning: 1 if truck k is used, 0 otherwise
    m = model.addVars((k for k in range(K)), vtype=GRB.BINARY, name = 'm')

    #r_s number of technicians used for entire planning: 1 if technician is used, 0 otherwise
    r = model.addVars((s for s in R_s), vtype=GRB.BINARY, name = 'r')

    #v_k_t truck k is used during day: 1 if used, 0 otherwise
    v = model.addVars(((t,k) for t in truckRange for k in range(K)), vtype=GRB.BINARY, name = 'v')

    #p_s_t technician s is used during day: 1 if used, 0 otherwise
    p = model.addVars(((t,s) for t in techRange for s in R_s), vtype=GRB.BINARY, name = 'p')

    #w_i_t request i is delivered on day: 1 if delivered, 0 otherwise
    w = model.addVars(((t,i) for t in truckRange for i in R), vtype=GRB.BINARY, name = 'w')

    #y_i_t request i is installed on day: 1 if installed, 0 otherwise
    y = model.addVars(((t,i) for t in techRange for i in R), vtype=GRB.BINARY, name = 'y')

    #upper bound weights of machine
    q = model.addVars(((i,k) for i in R_0 for k in range(K)), vtype=GRB.INTEGER, name = 'q')

    #g_is number of visits done by technician
    g = model.addVars(((i, s) for s in R_s for i in R_s[s]),vtype=GRB.INTEGER, name='g')

    #b_i number of days installation of request j is delayed after its delivery
    b = model.addVars(((i) for i in R),vtype=GRB.INTEGER, name='b')

    # 1 Objective
    obj = quicksum(CV*m[k] for k in range(K)) + \
        quicksum(CVU*v[t,k] for t in truckRange for k in range(K)) + \
        quicksum(CVT*calc_dist(R_0.get(i),R_0.get(j))*x[t,k,i,j] for k in range(K) for t in truckRange for i in R_0 if t<=l[i] and t>=e[i] for j in R_0 if t<=l[j] and t>=e[j] if i!=j) + \
        quicksum(CT*r[s] for s in R_s) + \
        quicksum(CTU*p[t,s] for t in techRange for s in R_s) + \
        quicksum(CTT*calc_dist(R_s[s][i],R_s[s][j])*z[t,s,i,j] for s in R_s for t in techRange for i in R_s[s] if t>=e[i]+1 for j in R_s[s] if t>=e[j]+1 if i!=j ) + \
        quicksum(CI_i[i]*b[i] for i in R)

    # 2 arcs entering location = arcs exiting location
    for t in truckRange:
        for k in range(K):
            for i in R_0:
                if t<=l[i] and t>=e[i]:
                    model.addConstr(quicksum(x[t,k,i,j] for j in R_0 if i!=j and t<=l[j] and t>=e[j]) == quicksum(x[t,k,j,i] for j in R_0 if i!=j and t<=l[j] and t>=e[j]))

    # 3 start and end routes at depot
    for t in truckRange:
            for k in range(K):
                model.addConstr(quicksum(x[t,k,i,'depot'] for i in R if t<=l[i] and t>=e[i]) == quicksum(x[t,k,'depot',i] for i in R if t<=l[i] and t>=e[i]))

    # 3.1
    for t in truckRange:
            for k in range(K):
                model.addConstr(quicksum(x[t,k,i,'depot'] for i in R if t<=l[i] and t>=e[i]) <= M[t]*v[t,k])

    # 4 Max distance truck can drive
    for t in truckRange:
            for k in range(K):
                model.addConstr(quicksum(calc_dist(R_0.get(i),R_0.get(j))*x[t,k,i,j] for i in R_0 if t<=l[i] and t>=e[i] for j in R_0 if i!=j and t<=l[j] and t>=e[j]) <= D)

    # 5 Truck must be available
    model.addConstrs((v[t,k] <= m[k]) for k in range(K) for t in truckRange)

    # 6 Truck used for day and can travel
    for t in truckRange:
            for k in range(K):
                model.addConstrs(x[t,k,i,j]<=v[t,k] for i in R_0 if t<=l[i] and t>=e[i] for j in R_0 if i!=j and t<=l[j] and t>=e[j])

    # 7 Delivery timewindow
    for i in R:
        for t in range(e[i],l[i]+1):
            if t<=l[i] and t>=e[i]:
                model.addConstr(quicksum(x[t,k,i,j] for k in range(K) for j in R_0 if i!=j and t<=l[j] and t>=e[j])==(w[t,i]))

    # 8 Each request is delivered
    model.addConstrs(quicksum(w[t,i] for t in range(e[i],l[i]+1)) == 1 for i in R)

    # 9 Weight is removed after visiting request (subtour elimitation)
    for t in truckRange:
            for k in range(K):
                model.addConstrs(q[j,k] <= q[i,k]-(x[t,k,i,j])*(C+c_i[j])+C for i in R_0 if t<=l[i] and t>=e[i] for j in R if i!=j and t<=l[j] and t>=e[j])

    # 10 Max weight from truck
    model.addConstrs(q['depot',k]==C for k in range(K))

    # 11 A location should be visited by technician
    for t in techRange:
        for s in R_s:
            for i in R_s[s]:
                if t>=e[i]+1:
                    model.addConstr(quicksum(z[t,s,i,j] for j in R_s[s] if i!=j and t>=e[j]+1) == quicksum(z[t,s,j,i] for j in R_s[s] if i!=j and t>=e[j]+1))

    # 12 start and end route at home
    for t in techRange:
        for s in R_s:
            model.addConstr(quicksum(z[t,s,i,s] for i in R_s[s] if i!=s and t>=e[i]+1) == quicksum(z[t,s,s,i] for i in R_s[s] if i!=s and t>=e[i]+1))

    # 12.1
    for t in techRange:
        for s in R_s:
            model.addConstr(quicksum(z[t,s,i,s] for i in R_s[s] if i!=s and t>=e[i]+1) == p[t,s])

    # 13 Technician max distance
    for t in techRange:
        for s in R_s:
            model.addConstr(quicksum(calc_dist(R_s[s][i],R_s[s][j])*z[t,s,i,j] for i in R_s[s] if t>=e[i]+1 for j in R_s[s] if i!=j and t>=e[j]+1)<=D_s[s])

    # 14 Max number of installs
    for t in techRange:
        for s in R_s:
            model.addConstr(quicksum(z[t,s,i,j] for i in R_s[s] if t>=e[i]+1 for j in R_s[s] if i!=j and j!=s and t>=e[j]+1)<=N_s[s])

    # 15 Technician has been hired
    model.addConstrs(p[t,s]<=r[s] for t in techRange for s in R_s)

    # 16 Technician can travel between requests in one day
    for t in techRange:
        for s in R_s:
            model.addConstrs(z[t,s,i,j]<=p[t,s] for i in R_s[s] if t>=e[i]+1 for j in R_s[s] if i!=j and t>=e[j]+1)

    # 17 Machine can be installed one day after delivery
    for i in R:
        for t in range(e[i]+1,T+1):
            total = 0
            for s in R_s:
                for j in R_s[s]:
                    if i!=j and i in R_s[s] and t>=e[j]+1:
                        total+=z[t,s,i,j]
            model.addConstr(total==y[t,i])

    # 18 Each request is installed
    model.addConstrs(quicksum(y[t,i] for t in range(e[i]+1,T+1)) == 1 for i in R)

    # 19 subtours never form in technician routes.
    for t in techRange:
        for s in R_s:
            model.addConstrs(g[j,s] <= g[i,s]-(z[t,s,i,j])*(1+N_s[s])+N_s[s] for i in R_s[s] if t>=e[i]+1 for j in R_s[s] if i!=j and j!=s and t>=e[j]+1)

    # 20 Max number of visits technician per day
    model.addConstrs(g[s,s]==N_s[s] for s in R_s)

    # 21 Technician can work 4 consecutive days but rest 1 day
    model.addConstrs(quicksum(p[u,s] for u in range(t,t+4+1)) <=5-p[t+5,s] for s in R_s for t in range(2,T+1-5))

    # 22 Technician can work 5 consecutive days but rest 2 days
    model.addConstrs(quicksum(p[u,s] for u in range(t,t+4+1)) <=5-p[t+6,s] for s in R_s for t in range(2,T+1-6))

    # 23 Prevents technicians from working more than 5 days in the last 6 days
    model.addConstrs(quicksum(p[u,s] for u in range(T-5+2,T)) <=5-p[T,s] for s in R_s)

    # 24 Calculates b (idling time)
    model.addConstrs(quicksum(t*y[t,i] for t in range(e[i]+1,T+1))-quicksum(t*w[t,i] for t in range(e[i],l[i]+1))-1==b[i] for i in R)

    # 25 Objective
    model.setObjective(obj,GRB.MINIMIZE)

    model.Params.LogToConsole = False
    model.setParam('TimeLimit', max_seconds)
    model.setParam('MIPFocus',1)
    model.optimize()

    x_sol = {key: value for key, value in model.getAttr("x",x).items() if value >= 0.5}
    z_sol = {key: value for key, value in model.getAttr("x",z).items() if value >= 0.5}

    return x_sol, z_sol