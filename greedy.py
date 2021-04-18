from InstanceVerolog2019 import InstanceVerolog2019
import classes
import extraction
import math
import sys
import operator

def solve(file):

    instance = extraction.extract(file)
    solution = classes.Solution(instance.Days)

    # --- FUNCTIONS NEEDED --- #

    # return euclidan distance
    def euclidean(xa,ya,xb,yb):
        return math.ceil(math.sqrt(math.pow((xa-xb),2) + math.pow((ya-yb),2)))

    # Insert new location in route. e.g. [1,2,1] -> [1,2,3,1]
    def insert_in_route(location,route):
        old_route = []
        for item in route:
            old_route.append(item)
        old_route.insert(-1,location)
        return old_route

    # Make a dict from locations instead of objects
    # This should probably be done in extraction .py
    def make_location_dict():
        locdict = dict()
        for loc in instance.Locations:
            locdict[loc.ID] = (loc.X,loc.Y)
        return locdict

    # Convert a route list eg. [0,1,2,0] to a list of coordinates eg. [[0,0],[120,120],[320,456],[0,0]]
    def route_to_coordinates(routelist):
        locdict = make_location_dict()
        coordinate_list = []
        for loc in routelist:
            coordinate_list.append([locdict.get(loc)[0], locdict.get(loc)[1]])
        return coordinate_list

    # Calculate distance needed to travel route
    def calc_route_distance(routelist):
        #print(routelist)
        coordinate_list = route_to_coordinates(routelist)
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

    requests_in_trucks = []
    requests_technicianed = []
    requests_allocated = []

    # --- ALGORITHM --- #


    # --- TRUCKS ---#
    # Loop through each day
    for day in solution.Days:
    #   print("Day: ", day.dayNumber)
        trucksUsed = []
        trucksUsed.append(classes.Truck(len(trucksUsed) + 1, day.dayNumber,0,instance.TruckDayCost,instance.TruckCost))
        currentTruck = 0
        # Loop through requests to allocate trucks
        for request in instance.Requests:
            # check if request has already been allocated or first day is later then today
            if request in requests_in_trucks or request.firstDay > day.dayNumber:
                continue
            satisfied = 0
            # Constraint 1: Item should fit
            current_cap = get_used_capacity(trucksUsed[currentTruck], instance)
            machine_cap = instance.Machines[request.machineID-1].size * request.amount
            if ((current_cap + machine_cap) < instance.TruckCapacity):
                satisfied += 1
            # Constraint 2: Car should have enough gas to take route
            current_route = trucksUsed[currentTruck].route
            new_route = insert_in_route(request.locID,trucksUsed[currentTruck].route)
            if calc_route_distance(new_route)  <= instance.TruckMaxDistance:
                satisfied += 1
            # Constraint 3: First end day in truck can not be later than last start day of new item. Thus:
            if request.firstDay < trucksUsed[currentTruck].getFirstEndDay():
                satisfied += 1
            # Allocate to either current or new truck
            if satisfied == 3:
                trucksUsed[currentTruck].machines.append(instance.Machines[request.machineID - 1])
                trucksUsed[currentTruck].requests.append(request)
                trucksUsed[currentTruck].route = new_route
                # print("-->inserted ", new_route)
                day.TruckRequests.append(request)
            # Else make new truck
            else:
                solution.Days[day.dayNumber - 1].Trucks.append(trucksUsed[currentTruck])
                trucksUsed.append(classes.Truck( len(trucksUsed) + 1, day.dayNumber, 0, instance.TruckDayCost, instance.TruckCost))
                currentTruck += 1
                trucksUsed[currentTruck].machines.append(instance.Machines[request.machineID - 1])
                trucksUsed[currentTruck].requests.append(request)
                trucksUsed[currentTruck].route = insert_in_route(request.locID,trucksUsed[currentTruck].route)
                day.TruckRequests.append(request)
            requests_in_trucks.append(request)
            satisfied = 0
        if trucksUsed[currentTruck].requests:
            solution.Days[day.dayNumber - 1].Trucks.append(trucksUsed[currentTruck])

        # Add truck to solution days if it has requests
        if not trucksUsed[0].requests:
            continue
        for truck in trucksUsed:
            solution.Days[day.dayNumber - 1].TruckRoutes += [truck.route]
        solution.Days[day.dayNumber - 1].NrTruckRoutes = len(trucksUsed)

    # End result: solution.Days now contains solutionday objects which contain the truck objects which contain their
    # routes and the request objects that they will serve



    # --- TECHNICIANS --- #
    jobs_next_day = []
    jobs_this_day = []
    jobs_allocated = []
    technicians = [technician for technician in instance.Technicians]
    for day in solution.Days:
        print("----------Day: ", day.dayNumber)
        # initialise day
        jobs_this_day = jobs_next_day
        jobs_next_day = []
        technicians_used = []
        for request in day.TruckRequests:
            jobs_next_day.append(request)
        # try to allocate jobs
        for job in jobs_this_day:
            print("Job: ", job.ID)
            if job.ID == 6:
                pass
            if job.ID in jobs_allocated:
                print("Job already allocated, next...")
                continue
            for technician in instance.Technicians:
                print('Trying technician: ', technician.ID)
                current_jobz = [req.ID for req in technician.requests.get(day.dayNumber)]
                current_diz = calc_route_distance(technician.routes.get(day.dayNumber))
                print('Current jobs for technician: ', current_jobz)
                print('Current distance for technician: ', current_diz)
                print('Max distance for technician: ', technician.maxDistance)
                satisfied = 0
                # Constraint 1: Technicians should be available:
                if technician.available:
                    satisfied += 1
                    print("#1 - Days worked constraint satisfied")
                # Constraint 2: Technician should be able to fix machine
                if job.machineID in technician.machines:
                    satisfied += 1
                    print("#2 - Machine installment constraint satisfied")
                # Constraint 3: Technician should be able to travel
                new_route = insert_in_route(job.locID, technician.routes.get(day.dayNumber))
                print('New route: ', new_route)
                print('Distance of new route: ', calc_route_distance(new_route))
                if calc_route_distance(new_route) <= technician.maxDistance:
                    satisfied += 1
                    print('#3 - Distance constraint satisfied')
                # Constraint 4: Technician should be able to install
                if technician.installs < technician.maxInstalls:
                    satisfied += 1
                    print('#4 - Max installs constraint satisfied')
                print('Total constraints satisfied: ', satisfied)
                if satisfied == 4:
                    print("Allocated to techician: ", technician.ID)
                    technician.requests.get(day.dayNumber).append(job)
                    technician.routes[day.dayNumber] = new_route
                    technician.installs += 1
                    technician.daysWorked += 1
                    jobs_allocated.append(job)
                    if technician not in technicians_used:
                        technicians_used.append(technician)
                    break
        # end of day
        day.NrTechnicianRoutes = len(technicians_used)
        for technician in technicians:
            technician.set_available(day.dayNumber)
            if technician in technicians_used:
                day.Technicians.append(technician)
                technician.installs = 0
        technicians_used = []
        for job in jobs_this_day:
            if job not in jobs_allocated:
                jobs_next_day.append(job)

    # --- Final check --- #


    original_stdout = sys.stdout
    with open('solution.txt', 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print('DATASET = ORTEC Caroline VeRoLog 2019')
        print('NAME = Instance 20')
        print(' ')
        for day in solution.Days:
            print("DAY = ", day.dayNumber)
            print("NUMBER_OF_TRUCKS = ", len(day.TruckRoutes))
            for truck in day.Trucks:
                prnt = str(truck.ID)
                for req in truck.requests:
                    prnt += ' ' + str(req.ID)
                if truck.requests:
                    print(prnt)
            print("NUMBER_OF_TECHNICIANS =  ", day.NrTechnicianRoutes)
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



    '''   class SolutionDay(object):
            def __init__(self, dayNr):
                self.dayNumber = dayNr
                self.NrTruckRoutes = None
                self.TruckRoutes = []
                self.NrTechnicianRoutes = None
                self.TechnicianRoutes = []
                self.TruckRequests = []'''



        # Loop through requests again to allocate technicians

    '''   self.ID = ID
            self.locID = locID
            self.firstDay = firstDay
            self.LastDay = LastDay
            self.machineID = machineID
            self.amount = amount
    '''