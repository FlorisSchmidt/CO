import sys
import extraction
from InstanceVerolog2019 import InstanceVerolog2019

def main():
    try:
        instance_file = sys.argv[1]
        max_time = sys.argv[2]
        instance = InstanceVerolog2019(instance_file)
        Requests, Machines, Technicians = extraction.extract(instance)
    except:
        print('Missing argument')

main()