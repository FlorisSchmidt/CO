class Solution(object):
    def __init__(self,Days):
        self.Days = []
        self.givenCost = self.SolutionCost()
        self.calcCost = self.SolutionCost()


    class SolutionDay(object):
            def __init__(self, dayNr):
                self.dayNumber = dayNr
                self.NrTruckRoutes = None
                self.TruckRoutes = []
                self.NrTechnicianRoutes = None
                self.TechnicianRoutes = []

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
            self.Route = []
            self.calcDistance = None

    class TechnicianRoute(object):
        def __init__(self):
            self.ID = None
            self.Route = []
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
        self.LastDay = LastDay
        self.machineID = machineID
        self.amount = amount

class Technician(object):
    def __init__(self, ID, locID,maxDistance, maxInstals, machines):
        self.ID = ID
        self.locID = locID
        self.machines = machines


class Truck(object):
    def __init__(self, ID, day, route, distanceCost, dayCost, cost):
        self.ID = ID
        self.dayNum = day
        self.route = route
        self.distanceCost = distanceCost
        self.dayCost = dayCost
        self.cost = cost
        self.machines = []