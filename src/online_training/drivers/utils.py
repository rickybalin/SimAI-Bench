from typing import List
import os

def parseNodeList(scheduler: str) -> List[str]:
    """
    Parse the node list provided by the scheduler

    :param scheduler: scheduler descriptor
    :type scheduler: str
    :return: tuple with node list and number of nodes
    :rtype: tuple
    """
    nodelist = []
    if scheduler=='pbs':
        hostfile = os.getenv('PBS_NODEFILE')
        with open(hostfile) as file:
            nodelist = file.readlines()
            nodelist = [line.rstrip() for line in nodelist]
            nodelist = [line.split('.')[0] for line in nodelist]
    return nodelist

