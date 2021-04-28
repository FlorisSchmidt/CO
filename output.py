import sys
import operator

def print_solution(solution, solutionname):
    original_stdout = sys.stdout
    with open('{} solution.txt'.format(str(solutionname)).replace(" ","_"), 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print('DATASET = ORTEC Caroline VeRoLog 2019')
        print('NAME = Instance 20\n')
        for day in solution.Days:
            print("DAY = " + str(day.dayNumber))
            print("NUMBER_OF_TRUCKS = " + str(len(day.TruckRoutes)))
            for truck in day.Trucks:
                prnt = str(truck.ID)
                for req in truck.requests:
                    prnt += ' ' + str(req.ID)
                if truck.requests:
                    print(prnt)
            print("NUMBER_OF_TECHNICIANS =  " +  str(day.NrTechnicianRoutes))
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