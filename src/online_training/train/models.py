##### 
##### Wrapper functions for the avaliable models to initialize them
##### and load/create their required data structures 
#####
from typing import Tuple
from omegaconf import DictConfig
import numpy as np
import torch
import torch.nn as nn
import numpy as np

from .mlp.model import MLP
from .gnn.model import GNN


def load_model(cfg: DictConfig, comm, client, rng) -> Tuple[nn.Module, np.ndarray]: 
    """ 
    Return the selected model and its training data

    :param cfg: DictConfig with training configuration parameters
    :param comm: Class containing the MPI communicator information
    :param rng: numpy random number generator
    :return: touple with the model and the data
    """

    # Instantiate model
    if (cfg.model=="mlp"):
        model  = MLP(inputDim=cfg.mlp.inputs, outputDim=cfg.mlp.outputs,
                     numNeurons=cfg.mlp.neurons, numLayers=cfg.mlp.layers)
    elif (cfg.model=="gnn"):
        model = GNN(cfg)
        model.setup_local_graph(client, comm.rank)

    # Load/Generate training data
    if not cfg.online.backend:
        if (cfg.data_path == "synthetic"):
            data = model.create_data(cfg, rng)
        else:
            data = model.load_data(cfg, comm)
    else:
        data = np.array([0])

    return model, data 



