#!/bin/bash

# Set env
#source /eagle/datascience/balin/SimAI-Bench/env_dragon.sh
echo Loaded modules:
module list

# Set executables
BASE_DIR=/eagle/datascience/balin/SimAI-Bench/SimAI-Bench
DRIVER=$BASE_DIR/src/online_training/drivers/dragon_driver.py
SIM_EXE=$BASE_DIR/src/online_training/data_producers/sim.py
ML_EXE=$BASE_DIR/src/online_training/train/train.py
DRIVER_CONFIG_PATH=$PWD/conf
DRIVER_CONFIG_NAME="dragon_config_gnn"
TRAIN_CONFIG_PATH=$PWD/conf
TRAIN_CONFIG_NAME="train_config_gnn_debug"

# Set up run
NODES=$(cat $PBS_NODEFILE | wc -l)
DICT_NODES=1
SIM_NODES=1
SIM_PROCS_PER_NODE=2
SIM_RANKS=$((SIM_NODES * SIM_PROCS_PER_NODE))
ML_NODES=1
ML_PROCS_PER_NODE=2
ML_RANKS=$((ML_NODES * ML_PROCS_PER_NODE))
JOBID=$(echo $PBS_JOBID | awk '{split($1,a,"."); print a[1]}')
echo Number of total nodes: $NODES
echo Number of dictionary nodes: $DICT_NODES
echo Number of simulation nodes: $SIM_NODES
echo Number of ML training nodes: $ML_NODES
echo Number of simulation ranks per node: $SIM_PROCS_PER_NODE
echo Number of simulation total ranks: $SIM_RANKS
echo Number of ML ranks per node: $ML_PROCS_PER_NODE
echo Number of ML total ranks: $ML_RANKS
echo

# Sent env vars

# Run
SIM_ARGS="--backend\=dragon --model\=gnn --problem_size\=debug --launch\=colocated --ppn\=${SIM_RANKS} --tolerance\=0.002"
dragon $DRIVER --config-path $DRIVER_CONFIG_PATH --config-name $DRIVER_CONFIG_NAME \
    deployment="colocated" \
    dict.num_nodes=$DICT_NODES sim.num_nodes=$SIM_NODES train.num_nodes=$ML_NODES \
    sim.executable=$SIM_EXE sim.arguments="${SIM_ARGS}" \
    sim.procs=${SIM_RANKS} sim.procs_pn=${SIM_PROCS_PER_NODE} \
    train.executable=$ML_EXE train.config_path=${TRAIN_CONFIG_PATH} train.config_name=${TRAIN_CONFIG_NAME} \
    train.procs=${ML_RANKS} train.procs_pn=${ML_PROCS_PER_NODE} 

    
