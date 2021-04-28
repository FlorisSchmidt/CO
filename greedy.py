from InstanceVerolog2019 import InstanceVerolog2019
import classes
import math
import functions

def solve(instance):

    solution = classes.Solution(instance.Days)
    requests_in_trucks = []
    requests_technicianed = []
    requests_allocated = []

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
            current_cap = functions.get_used_capacity(trucksUsed[currentTruck], instance)
            machine_cap = instance.Machines[request.machineID-1].size * request.amount
            current_route = trucksUsed[currentTruck].route
            new_route = functions.insert_in_route(request.locID,trucksUsed[currentTruck].route)

            # Constraint 1: Item should fit
            # Constraint 2: Car should have enough gas to take route
            # Constraint 3: First end day in truck can not be later than last start day of new item. Thus:

            # Allocate to either current or new truck
            if (
                ((current_cap + machine_cap) < instance.TruckCapacity) and
                (functions.calc_route_distance(new_route,instance.Locations) <= instance.TruckMaxDistance) and
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
                trucksUsed[currentTruck].route = functions.insert_in_route(request.locID,trucksUsed[currentTruck].route)
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
            if job.ID in jobs_allocated:
                continue
            for technician in instance.Technicians:
                current_jobz = [req.ID for req in technician.requests.get(day.dayNumber)]
                current_diz = functions.calc_route_distance(technician.routes.get(day.dayNumber),instance.Locations)
                # Constraint 1: Technicians should be available:
                # Constraint 2: Technician should be able to fix machine
                # Constraint 3: Technician should be able to travel
                # Constraint 4: Technician should be able to install
                new_route = functions.insert_in_route(job.locID, technician.routes.get(day.dayNumber))
                if (technician.available and 
                    job.machineID in technician.machines and
                    functions.calc_route_distance(new_route,instance.Locations) <= technician.maxDistance and
                    technician.installs < technician.maxInstalls
                ):
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