import extraction
import classes
import functions
from InstanceVerolog2019 import InstanceVerolog2019

def solve(file):
    instance = InstanceVerolog2019(file)
    instance = extraction.extract(instance)
    solution = classes.Solution(instance.Days)

    max = 0
    scheduledRequest = []
    (x_base,y_base) = instance.Locations.get(1)

    for (x,y) in instance.Locations.values():
        dist = functions.euclidean(x,y,x_base,y_base)
        if dist > max:
            max = dist
        
    #Calc difficulty for all requests
    def calculate_difficulty(request,alpha=1,beta=1):
        (x,y) = instance.Locations.get(request.locID)
        request.difficulty = alpha*functions.euclidean(x,y,x_base,y_base)/max+beta*instance.Machines[request.machineID-1].size*request.amount/instance.TruckCapacity

    def possibleDelivery(Day):
        possibleRequests = []
        for request in instance.Requests:
            if request.firstDay<=Day and request.lastDay>=Day:
                possibleRequests.append(request)
        return possibleRequests


    for request in instance.Requests:
        calculate_difficulty(request)

    #Sort instances based on highest difficulty
    instance.Requests.sort(key=lambda x: x.difficulty, reverse=True)
    pivot = instance.Requests[0]
    scheduledRequest.append(pivot)

    #Get all requests that can be served that day
    possibleRequests = possibleDelivery(pivot.firstDay)
    possibleRequests = [x for x in possibleRequests if x not in scheduledRequest]

    #Add new truck to solution day corresponing to first day of pivot
    solution.Days[pivot.firstDay-1].Trucks.append(classes.Truck(len(solution.Days[pivot.firstDay-1].Trucks) + 1, pivot.firstDay-1,0,instance.TruckDayCost,instance.TruckCost))    

solve('instances 2021\CO_Case2021_14.txt')