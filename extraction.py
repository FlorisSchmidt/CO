from classes import Machine, Request, Technician

def extract(instance):
    Machines = []
    Requests = []
    Tech = []

    for machine in instance.Machines:
        machine = str(machine).split()
        ID = machine[0]
        size = machine[1]
        penalty = machine[2]
        Machines.append(Machine(ID,size,penalty))

    for technician in instance.Technicians:
        technician = str(technician).split()
        ID = technician[0]
        locID = technician[1]
        maxDistance = technician[2]
        maxInstals = technician[3]
        machines = technician[4:]
        Machines = []
        machineID = 1
        for machine in machines:
            if(int(machine)==1):
                Machines.append(machineID)
            machineID+=1
        Tech.append(Technician(ID,locID,maxDistance,maxInstals,Machines))

    for request in instance.Requests:
        request = str(request).split()
        ID = request[0]
        locID = request[1]
        firstDay = request[2]
        lastDay = request[3]
        machineID = request[4]
        amount = request[5]
        request = Request(ID,locID,firstDay,lastDay,machineID,amount)
        Requests.append(request)

    return Requests, Machines, Tech