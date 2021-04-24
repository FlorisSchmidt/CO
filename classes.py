class Solution(object):
    def __init__(self, Days):
        self.Days = []
        for i in range(Days):
            self.Days.append(self.SolutionDay(i+1))
        self.givenCost = self.SolutionCost()
        self.calcCost = self.SolutionCost()

    class SolutionDay(object):
        def __init__(self, dayNr):
            self.dayNumber = dayNr
            self.NrTruckRoutes = []
            self.TruckRoutes = []
            self.Trucks = []
            self.Technicians = []
            self.NrTechnicianRoutes = []
            self.TechnicianRoutes = []
            self.TruckRequests = []
            self.TechnicianRequests = []

    class SolutionCost(object):
        def __init__(self):
            self.TruckDistance = None
            self.NrTruckDays = None
            self.NrTrucksUsed = None
            self.TechnicianDistance = None
            self.NrTechnicianDays = None
            self.NrTechniciansUsed = None
            self.IdleMachineCost = None
            self.Cost = None

            self.TruckDistanceCumulative = None
            self.NrTruckDaysCumulative = None
            self.NrTrucksUsedCumulative = None
            self.TechnicianDistanceCumulative = None
            self.NrTechnicianDaysCumulative = None
            self.NrTechniciansUsedCumulative = None
            self.IdleMachineCostCumulative = None
            self.CostCumulative = None

    class TruckRoute(object):
        def __init__(self):
            self.ID = None
            self.route = []
            self.calcDistance = None

    class TechnicianRoute(object):
        def __init__(self):
            self.ID = None
            self.route = []
            self.calcDistance = None


class Machine(object):
    def __init__(self, ID, size, penalty):
        self.ID = ID
        self.size = size
        self.penalty = penalty
        self.installed = False


class Locations(object):
    def __init__(self, ID, x, y):
        self.ID = ID
        self.x = x
        self.y = y


class Request(object):
    def __init__(self, ID, locID, firstDay, LastDay, machineID, amount):
        self.ID = ID
        self.locID = locID
        self.firstDay = firstDay
        self.lastDay = LastDay
        self.machineID = machineID
        self.amount = amount



class Technician(object):
    def __init__(self, ID, ndays, locID, maxDistance, maxInstalls, machines):
        self.ID = ID
        self.ndays = ndays
        self.locID = locID
        self.maxDistance = maxDistance
        self.maxInstalls = maxInstalls
        self.machines = machines
        self.installs = 0
        self.daysWorked = 0
        self.routes = dict()
        self.requests = dict()
        self.available = True

        for i in range(1, ndays + 1):
            self.routes[i] = [locID, locID]
        for i in range(1, ndays + 1):
            self.requests[i] = []

    def set_available(self, daynum):
        if self.daysWorked > 4:
            self.available = False
        if not self.requests.get(daynum):
            self.available = True

class Truck(object):
    def __init__(self, ID, day, distanceCost, dayCost, cost):
        self.ID = ID
        self.dayNum = day
        self.route = [1, 1]
        self.distanceCost = distanceCost
        self.dayCost = dayCost
        self.cost = cost
        self.machines = []
        self.requests = []


    def getFirstEndDay(self):
        end_day = 10000
        for request in self.requests:
            if request.lastDay < end_day:
                end_day = request.lastDay
        return end_day

    def getLastStartDay(self):
        start_day = 0
        for request in self.requests:
            if request.FirstDay < start_day:
                start_day = request.FirstDay
        return start_day
