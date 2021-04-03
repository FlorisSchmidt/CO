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
        