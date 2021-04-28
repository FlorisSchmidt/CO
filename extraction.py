from classes import Machine, Request, Technician

def extract(instance):
    instance.extractedMachines = []
    instance.extractedRequests = []
    instance.extractedTechnicians = []

    for machine in instance.Machines:
        machine = str(machine).split()
        ID = int(machine[0])
        size = int(machine[1])
        penalty = int(machine[2])
        instance.extractedMachines.append(Machine(ID,size,penalty))

    for technician in instance.Technicians:
        technician = str(technician).split()
        ID = int(technician[0])
        ndays = instance.Days
        locID = int(technician[1])
        maxDistance = int(technician[2])
        maxInstals = int(technician[3])
        machines = technician[4:]
        Machines = []
        machineID = 1

        for machine in machines:
            if(int(machine)==1):
                Machines.append(machineID)
            machineID+=1
        instance.extractedTechnicians.append(Technician(ID,ndays,locID,maxDistance,maxInstals,Machines))

    for request in instance.Requests:
        request = str(request).split()
        ID = int(request[0])
        locID = int(request[1])
        firstDay = int(request[2])
        lastDay = int(request[3])
        machineID = int(request[4])
        amount = int(request[5])
        size = instance.extractedMachines[machineID - 1].size * amount
        request = Request(ID,locID,firstDay,lastDay,machineID,amount,size)
        instance.extractedRequests.append(request)

    locdict = dict()
    for loc in instance.Locations:
        locdict[loc.ID] = (loc.X,loc.Y)

    instance.Locations = locdict
    instance.Machines = instance.extractedMachines
    instance.Requests = instance.extractedRequests
    instance.Technicians = instance.extractedTechnicians

    return instance