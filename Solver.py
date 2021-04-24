import argparse
import extraction
import greedy
import output
from InstanceVerolog2019 import InstanceVerolog2019


#import signal

# Only works with mac OS
# def set_run_timeout(timeout):
#     """Set maximum execution time of the current Python process"""
#     def alarm(*_):
#         raise SystemExit("Timed out!")
#     signal.signal(signal.SIGALRM, alarm)
#     signal.alarm(timeout)

def main():
    #NOTE IN FINAL VERSION - BEFORE ARGUMENTS MUST BE REMOVED (THIS MAKES THEM OPTIONAL)
    parser = argparse.ArgumentParser(description='Solve Verolog 2019 problem instances')
    parser.add_argument('instancefile', type=str,help='The problem instance', default='all')
    parser.add_argument('maxtime', type=int, help='The max time the solver is allowed to run', default=100)
    args = parser.parse_args()

    # set_run_timeout(int(args.maxtime))
    if (args.instancefile=='all'):
        import glob
        for file in glob.glob("instances 2021/*.txt"):
            instance = InstanceVerolog2019(file)
            solution = greedy.solve(extraction.extract(instance))
            output.print_solution(solution,instance.Name)
    else:
        instance = InstanceVerolog2019(args.instancefile)
        solution = greedy.solve(extraction.extract(instance))
        output.print_solution(solution)


if __name__ == '__main__':
    main()