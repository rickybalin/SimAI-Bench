import os
import sys
from typing import Tuple, List
from omegaconf import DictConfig, OmegaConf
import hydra

import multiprocessing as mp
import dragon
from dragon.data.distdictionary.dragon_dict import DragonDict
from dragon.native.process_group import ProcessGroup
from dragon.native.process import TemplateProcess, MSG_PIPE, MSG_DEVNULL

from online_training.data_producers.sim import main as sim
from online_training.train.train import main as train

## Define function to parse node list
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


#def sim_mpi_worker(q, sim_args):
#    dd = q.get()
#    sim(dd, sim_args)

## Colocated launch
def launch_colocated(cfg: DictConfig, dd: DragonDict, nodelist: List[str]) -> None:
    """
    Launch the workflow with the colocated deployment

    :param cfg: hydra config
    :type cfg: DictConfig
    :param dd: Dragon Didtributed Dictionary
    :type dd: DragonDict
    :param nodelist: node list provided by scheduler
    :type nodelist: List[str]
    """
    # Print nodelist
    if (nodelist is not None):
        print(f"\nRunning on {len(nodelist)} total nodes")
        print(nodelist, "\n")
        hosts = ','.join(nodelist)

    # Pass DDict to simulation through a queue
    #dd_q = mp.Queue(maxsize=cfg.sim.procs)
    #for _ in range(cfg.sim.procs):
    #    dd_q.put(dd)
    dd_serialized = dd.serialize()

    # Set up and launch the simulation component
    sim_args = []
    if (cfg.sim.executable.split("/")[-1].split('.')[-1]=='py'):
        sim_exe = sys.executable
        sim_args.append(cfg.sim.executable.split("/")[-1])
    sim_args.append(cfg.sim.arguments)
    sim_args.append(f' --dictionary={dd_serialized}')
    sim_run_dir = '/'.join(cfg.sim.executable.split("/")[:-1])

    sim_grp = ProcessGroup(restart=False, pmi_enabled=True)
    sim_grp.add_process(nproc=1, 
                    template=TemplateProcess(target=sim_exe, 
                                             args=sim_args, 
                                             cwd=sim_run_dir, 
                                             stdout=MSG_PIPE))
    sim_grp.add_process(nproc=cfg.sim.procs - 1,
                    template=TemplateProcess(target=sim_exe, 
                                             args=sim_args, 
                                             cwd=sim_run_dir, 
                                             stdout=MSG_DEVNULL))
    sim_grp.init()
    sim_grp.start()

    # Setup and launch the distributed training component
    ml_args = []
    ml_exe = sys.executable
    ml_args.append(cfg.train.executable.split("/")[-1])
    if (cfg.train.config_path): ml_args += f' --config-path {cfg.train.config_path}'
    if (cfg.train.config_name): ml_args += f' --config-name {cfg.train.config_name}'
    ml_args.append(f' ppn={cfg.train.mlprocs_pn}' \
                    + f' online.simprocs={cfg.sim.procs}' \
                    + f' online.backend=dragon' \
                    + f' online.dragon.launch={cfg.deployment}' \
                    + f' online.dragon.dictionary={dd_serialized}'
    )
    ml_run_dir = '/'.join(cfg.train.executable.split("/")[:-1])

    ml_grp = ProcessGroup(restart=False, pmi_enabled=True)
    ml_grp.add_process(nproc=1, 
                    template=TemplateProcess(target=ml_exe, 
                                             args=ml_args, 
                                             cwd=ml_run_dir, 
                                             stdout=MSG_PIPE))
    ml_grp.add_process(nproc=cfg.train.procs - 1,
                    template=TemplateProcess(target=ml_exe, 
                                             args=ml_args, 
                                             cwd=ml_run_dir, 
                                             stdout=MSG_DEVNULL))
    ml_grp.init()
    ml_grp.start()

    # Join both simulation and training
    sim_grp.join()
    sim_grp.stop()
    ml_grp.join()
    ml_grp.stop()


## Clustered DB launch
def launch_clustered(cfg, dd, nodelist) -> None:
    print("Not implemented yet")


## Main function
@hydra.main(version_base=None, config_path="./conf", config_name="dragon_config")
def main(cfg: DictConfig):
    # Assertions
    assert cfg.scheduler=='pbs' or cfg.scheduler=='local', print("Only allowed schedulers at this time are pbs and local")
    assert cfg.deployment == "colocated" or cfg.deployment == "clustered", \
                    print("Deployment is either colocated or clustered")

    # Get nodes of this allocation
    nodelist = parseNodeList(cfg.scheduler)

    # Start the Dragon Distributed Dictionary (DDict)
    mp.set_start_method("dragon")
    total_mem_size = cfg.dict.total_mem_size * (1024*1024*1024)
    dd = DragonDict(cfg.dict.managers_per_node, cfg.dict.num_nodes, total_mem_size)
    print("Launched the Dragon Dictionary \n", flush=True)
    
    if (cfg.deployment == "colocated"):
        print(f"Running with the {cfg.deployment} deployment \n")
        launch_colocated(cfg, dd, nodelist)
    elif (cfg.deployment == "clustered"):
        print(f"\nRunning with the {cfg.deployment} deployment \n")
        launch_clustered(cfg, dd, nodelist)
    else:
        print("\nERROR: Deployment is either colocated or clustered\n")

    # Close the DDict and quit
    dd.close()
    print("\nClosed the Dragon Dictionary and quitting ...", flush=True)


## Run main
if __name__ == "__main__":
    main()
