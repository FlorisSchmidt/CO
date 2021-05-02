import gurobipy as gp
import classes
import functions
import scipy.spatial.distance as distance
import pandas as pd
from gurobipy import GRB, quicksum

def solve(instance, max_seconds):
    solution = classes.Solution(instance.Days)

    model = gp.Model()

    def calc_dist(list_i,list_j):
        return functions.euclidean(list_i[0],list_j[0],list_i[1],list_j[1])
    #Sets
    R = {} #requests
    S = 0 #technicians
    S_0 = {} #starts with technicians locations then requests
    R_s = {}
    #Params
    T = instance.Days
    H_0 = [instance.Locations.get(1)[0],instance.Locations.get(1)[1]]
    D = instance.TruckMaxDistance
    #M_t = instance ?? Mt: upper bound on the number of visits a vehicle can do to depot on day t.
    M = {new_list: 0 for new_list in range(1,T+1)}
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
                can_install.append(request.ID-1)
            else:
                current_tech.append(0)
        can_install.append(len(S_0)+len(instance.Requests)-1)
        R_s[S-1] = can_install
        a_si.append(current_tech)
    
    R_0 = {}
    R_0[0] = H_0
    for request in instance.Requests:
        e.append(request.firstDay)
        l.append(request.lastDay)
        c_i.append(request.size)
        idle_cost = request.amount*instance.Machines[request.machineID-1].penalty
        CI_i.append(idle_cost)
        location = [instance.Locations.get(request.locID)[0],instance.Locations.get(request.locID)[1]]
        R[request.ID-1] = location
        R_0[request.ID] = location
        S_0[len(S_0)] = location
        for day in range(1,T+1):
            if(day>=request.firstDay and day<=request.lastDay):
                M[day]+=1

    K = max(M.values())
     # Requests and depot (at 0)
    
    #Decision variables
    #x_ij_k truck visits location j after location i: 1 if truck visits, 0 otherwise
    x = model.addVars(((t,k,i,j) for t in range(1,T+1) for k in range(K) for i in R_0 for j in R_0 if i!=j), vtype=GRB.BINARY, name='xij')

    z = model.addVars(((t,s,i,j) for t in range(1,T+1) for s in range(S) for i in R_s[s] for j in R_s[s] if i!=j), vtype=GRB.BINARY, name='zij')
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

    q = model.addVars(((i,k) for i in R_0 for k in range(K)), vtype=GRB.INTEGER, name = 'q')

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
        quicksum(CTT*calc_dist(S_0.get(i),S_0.get(j))*z[t,s,i,j] for s in range(S) for i in R_s[s] for j in R_s[s] if i!=j for t in range(1,T+1)) + \
        quicksum(CI_i[i]*b[i] for i in R)

    # 2 arcs entering location = arcs exiting location
    model.addConstrs(quicksum(x[t,k,i,j] for j in R_0 if i!=j) == quicksum(x[t,k,j,i] for j in R_0 if i!=j) for i in R_0 for k in range(K) for t in range(1,T+1))
    # 3 start and end routes at depot
    model.addConstrs(quicksum(x[t,k,0,i] for i in R if i!=0) == quicksum(x[t,k,i,0] for i in R if i!=0) for k in range(K) for t in range(1,T+1))

    # 3.1
    model.addConstrs(quicksum(x[t,k,0,i] for i in R if i!=0) <= M[t]*v[t,k] for k in range(K) for t in range(1,T+1))

    # 4 Max distance truck can drive
    model.addConstrs(quicksum(calc_dist(R_0.get(i),R_0.get(j))*x[t,k,i,j] for i in R_0 for j in R_0 if i!=j) <= D for k in range(K) for t in range(1,T+1))

    # 5 Truck must be available
    model.addConstrs((v[t,k] <= m[k]) for k in range(K) for t in range(1,T+1))

    # 6 Truck used for day and can travel
    model.addConstrs((x[t,k,i,j]<=v[t,k]) for i in R_0 for j in R_0 if i!=j for k in range(K) for t in range(1,T+1))

    # 7 Delivery timewindow
    model.addConstrs((quicksum(x[t,k,i,j] for k in range(K) for j in R_0 if i!=j))==(w[t,i]) for i in R for t in range(e[i],l[i]+1))

    # 8 Each request is delivered
    model.addConstrs(quicksum(w[t,i] for t in range(e[i],l[i]+1)) == 1 for i in R)

    # 9 Weight is removed after visiting request (subtour elimitation)
    model.addConstrs(q[j,k] <= q[i,k]-(x[t,k,i,j])*(C+c_i[j])+C for i in R_0 for j in R if i!=j for k in range(K) for t in range(1,T+1))

    # 10 Max weight from truck
    model.addConstrs(q[0,k]==C for k in range(K))

    # 11 A location should be visited by technician
    model.addConstrs(quicksum(z[t,s,i,j] for j in R_s[s] if i!=j) == quicksum(z[t,s,j,i] for j in R_s[s] if i!=j) for s in range(S) for i in R_s[s]  for t in range(1,T+1))

    # 12 start and end route at home
    model.addConstrs(quicksum(z[t,s,i,R_s[s][-1]] for i in R_s[s][:-1]) == quicksum(z[t,s,R_s[s][-1],i] for i in R_s[s][:-1]) for s in range(S) for t in range(1,T+1))

    # 12.1
    model.addConstrs(quicksum(z[t,s,i,R_s[s][-1]] for i in R_s[s][:-1]) == p[t,s] for s in range(S) for t in range(1,T+1))

    # 13 Technician max distance
    model.addConstrs(quicksum(calc_dist(S_0.get(i),S_0.get(j))*z[t,s,i,j] for i in R_s[s] for j in R_s[s] if i!=j)<=D_s[s] for t in range(1,T+1) for s in range(S))

    # 14 Max number of installs
    model.addConstrs(quicksum(z[t,s,i,j] for i in R_s[s] for j in R if i!=j)<=N_s[s] for t in range(1,T+1) for s in range(S))

    # 15 Technician has been hired
    model.addConstrs(p[t,s]<=r[s] for t in range(1,T+1) for s in range(S))

    # 16 Technician can travel between requests in one day
    model.addConstrs(z[t,s,i,j]<=p[t,s] for t in range(1,T+1) for s in range(S) for i in R_s[s] for j in R_s[s] if i!=j)

    # 17 Machine can be installed one day after delivery
    model.addConstrs(quicksum(z[t,s,i,j] for s in range(S) for j in R_s[s] if i!=j)==y[t,i] for i in R for t in range(1+e[i],T+1))

    # 18 Each request is installed
    model.addConstrs(quicksum(y[t,i] for t in range(e[i]+1,T+1) ) == 1 for i in R)

    # 19 subtours never form in technician routes.
    model.addConstrs(g[j,s] <= g[i,s]-(z[t,s,i,j])*(1+N_s[s])+N_s[s] for s in range(S) for i in R_s[s] for j in R if i!=j for t in range(1,T+1))

    # 20 Max number of visits technician per day
    model.addConstrs(g[s+len(R),s]==N_s[s] for s in range(S))

    # 21 Technician can work 4 consecutive days but rest 1 day
    model.addConstrs(quicksum(p[u,s] for u in range(t+1,t+4+1)) <=5-p[t+5,s] for s in range(S) for t in range(1,T+1-5))

    # 22 Technician can work 5 consecutive days but rest 2 days
    model.addConstrs(quicksum(p[u,s] for u in range(t+1,t+4+1)) <=5-p[t+6,s] for s in range(S) for t in range(1,T+1-6))

    # 23 Prevents technicians from working more than 5 days in the last 6 days
    model.addConstrs(quicksum(p[u,s] for u in range(T+1-5,T)) <=5-p[T,s] for s in range(S))

    # 24 Calculates b (idling time)
    model.addConstrs(quicksum(t*y[t,i] for t in range(e[i]+1+1,T+1))-quicksum(t*w[t,i] for t in range(e[i]+1,l[i]+1))-1==b[i] for i in R)

    # 25 Objective
    model.setObjective(obj,GRB.MINIMIZE)

    model.Params.LogToConsole = True
    model.Params.BestObjStop
    model._x = x
    model.setParam('TimeLimit', max_seconds)
    model.optimize()

    model.printAttr("x")

    sol = model.getAttr("x")
    x_sol = model.getAttr("x",x)
    z_sol = model.getAttr("x",z)

    x_sol_clean = {}
    z_sol_clean = {}
    for i in x_sol:
        value = x_sol[i]
        if value > 0.5:
            x_sol_clean[i] = value
    for i in z_sol:
        value = z_sol[i]
        if value > 0.5:
            z_sol_clean[i] = value

    def print_solution(x_sol_clean):

        df = pd.DataFrame(x_sol_clean.keys(),columns=['t','k','i','j'])
        for dayNr in range(1,T+1):
            day = df.loc[df['t'] == dayNr]
            truck_ids = df['k'].unique()
            for truck in truck_ids:
                routes = day.loc[day['k']==truck]
                
                
                truck_route = []
                last_point = 0
                for i in range(routes.shape[0]-1):
                    print(routes)
                    route = routes.loc[routes['i']==int(last_point)]
                    print(route)
                    if(route.shape[0]!=1):
                        route = route.head(1)
                    index = route.index[0]
                    routes = routes.drop([index], axis=0)
                    
                    next_point = route['j'].iloc[0]
                    last_point=next_point
                    #print(next_point)
                    truck_route.append(next_point)

                print(truck_route)
            

    print_solution(x_sol_clean)

    return model
