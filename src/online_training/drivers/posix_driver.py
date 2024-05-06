# general imports
import os
import sys 
from typing import List
from omegaconf import DictConfig, OmegaConf
import hydra
import subprocess

import utils


def launch_colocated(cfg: DictConfig, nodelist: List[str]) -> None:
    # Print nodelist
    nNodes = len(nodelist)
    if nodelist:
        print(f"\nRunning on {nNodes} total nodes")
        print(nodelist, "\n")
        hosts = ','.join(nodelist)

    # Set up and launch the simulation
    extension = cfg.sim.executable.split(".")[-1]
    if extension=="py":
        client_exe = sys.executable
        exe_args = ' '.join([cfg.sim.executable, cfg.sim.arguments])
    else:
        client_exe = cfg.sim.executable
        exe_args = cfg.sim.arguments
    if (cfg.scheduler=='local'):
        launcher = 'mpirun'
        launcher_args = f'-n {cfg.sim.procs}'
    sim_command_list = [launcher, launcher_args, client_exe, exe_args, '&']
    sim_command = ' '.join(sim_command_list)
    print(f'Running simulation with command\n{sim_command}\n')
    subprocess.Popen(sim_command_list, shell=False)



## Main function
@hydra.main(version_base=None, config_path="./conf", config_name="posix_config")
def main(cfg: DictConfig):
    # Assertions
    assert cfg.scheduler=='pbs' or cfg.scheduler=='local', print("Only allowed schedulers at this time are pbs and local")
    assert cfg.deployment == "colocated" or cfg.deployment == "clustered", \
                    print("Deployment is either colocated or clustered")

    # Get nodes of this allocation
    nodelist = utils.parseNodeList(cfg.scheduler)

    # Call appropriate launcher
    if (cfg.deployment == "colocated"):
        print(f"\nRunning with {cfg.deployment} deployment\n")
        launch_colocated(cfg, nodelist)
    elif (cfg.deployment == "clustered"):
        print(f"\nRunning with {cfg.database.deployment} deployment\n")
        launch_clustered(cfg, nodelist)
    else:
        print("\nERROR: Launcher is either colocated or clustered\n")

    # Quit
    print("Quitting")


## Run main
if __name__ == "__main__":
    main()
