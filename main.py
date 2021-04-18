import sys
import extraction
import greedy
from InstanceVerolog2019 import InstanceVerolog2019

def main():
    try:
        instance_file = sys.argv[1]
        max_time = sys.argv[2]
        instance = InstanceVerolog2019(instance_file)
        greedy.solve(instance)
    except:
        print('Missing argument')

main()