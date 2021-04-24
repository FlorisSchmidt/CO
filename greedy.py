from InstanceVerolog2019 import InstanceVerolog2019
import classes
import math

def solve(instance):

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

    # Convert a route list eg. [0,1,2,0] to a list of coordinates eg. [[0,0],[120,120],[320,456],[0,0]]
    def route_to_coordinates(routelist):
        coordinate_list = []
        for loc in routelist:
            coordinate_list.append([instance.Locations.get(loc)[0], instance.Locations.get(loc)[1]])
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
        trucksUsed = []
        trucksUsed.append(classes.Truck(len(trucksUsed) + 1, day.dayNumber,0,instance.TruckDayCost,instance.TruckCost))
        currentTruck = 0
        # Loop through requests to allocate trucks
        for request in instance.Requests:
            # check if request has already been allocated or first day is later then today
            if request in requests_in_trucks or request.firstDay > day.dayNumber:
                continue
            current_cap = get_used_capacity(trucksUsed[currentTruck], instance)
            machine_cap = instance.Machines[request.machineID-1].size * request.amount
            current_route = trucksUsed[currentTruck].route
            new_route = insert_in_route(request.locID,trucksUsed[currentTruck].route)

            # Constraint 1: Item should fit
            # Constraint 2: Car should have enough gas to take route
            # Constraint 3: First end day in truck can not be later than last start day of new item. Thus:

            # Allocate to either current or new truck
            if (
                ((current_cap + machine_cap) < instance.TruckCapacity) and
                (calc_route_distance(new_route) <= instance.TruckMaxDistance) and
                (request.firstDay < trucksUsed[currentTruck].getFirstEndDay())
                ):
                trucksUsed[currentTruck].machines.append(instance.Machines[request.machineID - 1])
                trucksUsed[currentTruck].requests.append(request)
                trucksUsed[currentTruck].route = new_route
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
        # initialise day
        jobs_this_day = jobs_next_day
        jobs_next_day = []
        technicians_used = []
        for request in day.TruckRequests:
            jobs_next_day.append(request)
        # try to allocate jobs
        for job in jobs_this_day:
            if job.ID == 6:
                pass
            if job.ID in jobs_allocated:
                continue
            for technician in instance.Technicians:
                current_jobz = [req.ID for req in technician.requests.get(day.dayNumber)]
                current_diz = calc_route_distance(technician.routes.get(day.dayNumber))
                satisfied = 0
                # Constraint 1: Technicians should be available:
                if technician.available:
                    satisfied += 1
                # Constraint 2: Technician should be able to fix machine
                if job.machineID in technician.machines:
                    satisfied += 1
                # Constraint 3: Technician should be able to travel
                new_route = insert_in_route(job.locID, technician.routes.get(day.dayNumber))
                if calc_route_distance(new_route) <= technician.maxDistance:
                    satisfied += 1
                # Constraint 4: Technician should be able to install
                if technician.installs < technician.maxInstalls:
                    satisfied += 1
                if satisfied == 4:
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
    return solution
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