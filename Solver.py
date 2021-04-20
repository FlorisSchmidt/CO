import sys
import extraction
import greedy
from InstanceVerolog2019 import InstanceVerolog2019

import signal

def set_run_timeout(timeout):
    """Set maximum execution time of the current Python process"""
    def alarm(*_):
        raise SystemExit("Timed out!")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(timeout)

def main():
    try:
        instance_file = sys.argv[1]
        max_time = sys.argv[2]
        set_run_timeout(int(max_time))
        instance = InstanceVerolog2019(instance_file)
        greedy.solve(instance)
    except:
        print('Missing argument')

main()