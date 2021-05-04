import sys
import operator
import pandas as pd



def print_solution(solution, solutionname):
    original_stdout = sys.stdout
    with open('{} solution.txt'.format(str(solutionname)).replace(" ","_"), 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print('DATASET = ORTEC Caroline VeRoLog 2019')
        print('NAME = Instance 20\n')
        for day in solution.Days:
            print("DAY = " + str(day.dayNumber))
            print("NUMBER_OF_TRUCKS = " + str(len(day.TruckRoutes)))
            for truck in day.Trucks:
                prnt = str(truck.ID)
                for req in truck.requests:
                    prnt += ' ' + str(req.ID)
                if truck.requests:
                    print(prnt)
            print("NUMBER_OF_TECHNICIANS =  " +  str(day.NrTechnicianRoutes))
            unsorted = day.Technicians
            sortz = sorted(unsorted, key=operator.attrgetter('ID'))
            for technician in sortz:
                id = technician.ID
                sting = str(id)
                requests_handeled = technician.requests[day.dayNumber]
                if requests_handeled:
                    for req in requests_handeled:
                        sting += ' ' + str(req.ID)
                print(sting)
            print('')
    sys.stdout = original_stdout # Reset the standard output to its original value

def print_model(x_sol,z_sol):
    x = pd.DataFrame(x_sol.keys(),columns=['t','k','i','j'])
    z = pd.DataFrame(z_sol.keys(),columns=['t','s','i','j'])

    for dayNr in range(1,z['t'].max()+1):
        day = x.loc[x['t'] == dayNr]
        truck_ids = x['k'].unique()
        day_route_trucks = {}
        for truck in truck_ids:
            routes_truck_k = day.loc[day['k']==truck]

            truck_route = []
            last_point = 'depot'
            for i in range(routes_truck_k.shape[0]-1):
                route = routes_truck_k.loc[routes_truck_k['i']==last_point]

                if(route.shape[0]!=1):
                    route = route.head(1)
                index = route.index[0]
                routes_truck_k = routes_truck_k.drop([index], axis=0)

                next_point = route['j'].iloc[0]
                last_point=next_point
                truck_route.append(next_point)
            
            if truck_route:
                day_route_trucks[truck] = truck_route

        t = z.loc[z['t'] == dayNr]
        tech_ids = z['s'].unique()
        day_route_tech = {}
        for tech in tech_ids:
            routes_tech_s = t.loc[t['s']==tech]
            tech_route = []

            last_node = tech
            for i in range(routes_tech_s.shape[0]-1):
                route_nodes = routes_tech_s.loc[routes_tech_s['i']==last_node]

                if(route_nodes.shape[0] != 1):
                    route_nodes = route_nodes.head(1)
                index = route_nodes.index[0]
                routes_tech_s = routes_tech_s.drop([index], axis=0)

                next_node = route_nodes['j'].iloc[0]
                last_node = next_node
                tech_route.append(next_node)

            if tech_route:
                    day_route_tech[tech] = tech_route

        print("DAY = {}".format(dayNr))
        print("NUMBER_OF_TRUCKS = {}".format(len(day_route_trucks)))
        for key in day_route_trucks:
            print("{} {}".format(key,day_route_trucks[key]))
        print("NUMBER_OF_TECHNICIANS = {}".format(len(day_route_tech)))
        for tkey in day_route_tech:
            print("{} {}".format(tkey,day_route_tech[tkey]))
        print("\n")
        

            
