class Day(object):
    def __init__(self, dayNum, Tools, nTools):
        self.dayNum = dayNum
        self.toolsStart = [Tools[i].amount for i in range(0, nTools)]
        self.toolsEnd = [Tools[i].amount for i in range(0, nTools)]
        self.numVehicles = 0
        self.Vehicles = []
        self.Technicians = []
    def __repr__(self):
        return '%s' % (self.Vehicles)

class Machine(object):
        def init(self, ID, x, y, kind, penalty, skill, installed, size, day):
        self.ID = ID
        self.x = x
        self.y = y
        self.kind = kind
        self.penalty = penalty
        self.skill = skill
        self.installed = installed
        self.size = size
        self.day = day


class Truck(object):
     def init(self, ID, day, route, distanceCost, dayCost, cost):
        self.ID = ID
        self.dayNum = day
        self.route = route
        self.distanceCost = distanceCost
        self.dayCost = dayCost
        self.cost = cost

class Technician(object):
    def init(self, ID, day, route, distanceCost, dayCost, cost):
        self.ID = ID
        self.dayNum = day
        self.route = route
        self.distanceCost = distanceCost
        self.dayCost = dayCost
        self.cost = cost


class Tool(object):
    def __init__(self, ID, weight, amount, cost):
        self.ID = ID
        self.weight = weight
        self.amount = amount
        self.cost = cost
    def __repr__(self):
        return '%d\t%d\t%d\t%d' % (self.ID, self.weight, self.amount, self.cost)

class Vehicle(object):
    def __init__(self, day, route, weight, distance):
        self.dayNum = day
        self.route = route
        self.weight = weight
        self.distance = distance
        self.depotVisits = []
        self.excessTools = []

    def __repr__(self):
        return '%d\t%s\t%s\t%s\t%s\t%s' % (self.dayNum, self.route, self.weight, self.distance, self.depotVisits, self.excessTools)

    def updateDepots(self):
        values = np.array(self.route)
        searchval = 0
        IDs = np.where(values == searchval)[0]
        self.depotVisits = list(IDs)

class Request(object):
    def __init__(self, ID, node, fromDay, toDay, numDays, tool, toolCount, size, maxDays):
        self.ID = ID
        self.node = node
        self.fromDay = fromDay
        self.toDay = toDay
        self.numDays = numDays
        self.tool = tool
        self.toolCount = toolCount
        self.size = size
        self.delivered = False
        self.pickedup = False
        if fromDay == toDay:
            self.oneDayTW = True
        else:
            self.oneDayTW = False
        self.dayDelivered = -1
        self.dayPickedup = -1
        self.maxDays = maxDays
        if toDay + numDays > maxDays:
            self.toDay = maxDays - numDays
    def __repr__(self):
        return '%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (self.ID,self.node,self.fromDay,self.toDay,self.numDays,self.tool,self.toolCount,self.size,self.dayDelivered, self.dayPickedup, self.delivered, self.pickedup)

class Tool(object):
    def __init__(self, ID, weight, amount, cost):
        self.ID = ID
        self.weight = weight
        self.amount = amount
        self.cost = cost
    def __repr__(self):
        return '%d\t%d\t%d\t%d' % (self.ID, self.weight, self.amount, self.cost)
