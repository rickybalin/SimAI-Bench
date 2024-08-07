from typing import Tuple, Optional
import logging
from gmpy2 import is_square
import numpy as np
import math
import os
from mpipartition import Partition

import mpi4py
mpi4py.rc.initialize = False
from mpi4py import MPI

PI = math.pi

# Generate training data for each model
def generate_training_data(args, comm, 
                           step: Optional[int] = 0) -> Tuple[np.ndarray, np.ndarray, dict]:
    """Generate training data for each model
    """
    rank = comm.Get_rank()
    size = comm.Get_size()
    random_seed = 12345 + 1000*rank
    rng = np.random.default_rng(seed=random_seed)
    if (args.problem_size=="debug"):
        n_samples = 512
        ndIn = 1
        ndTot = 2
        coords = rng.uniform(low=0.0, high=2*PI, size=n_samples)
        y = np.sin(coords)+0.1*np.sin(4*PI*coords)
        y = (y - (-1.0875)) / (1.0986 - (-1.0875)) # min-max scaling
        data = np.vstack((coords,y)).T
    elif (args.problem_size=="small"):
        #assert is_square(size) or size==1, "Number of MPI ranks must be square or 1"
        N = 32
        n_samples = N**2
        ndIn = 1
        ndTot = 2
        #x, y = partition_domain((-2*PI, 2*PI), (-2*PI, 2*PI), N, size, rank)
        partition = Partition(dimensions=2, comm=comm)
        part_origin = partition.origin
        part_extent = partition.extent
        x = np.linspace(part_origin[0],part_origin[0]+part_extent[0],num=N)*4*PI-2*PI
        y = np.linspace(part_origin[1],part_origin[1]+part_extent[1],num=N)*4*PI-2*PI
        x, y = np.meshgrid(x, y)
        coords = np.vstack((x.flatten(),y.flatten())).T
        r = np.sqrt(x**2+y**2)
        period = 60
        freq = 2*PI/period
        u = np.sin(2.0*r-freq*step)/(r+1.0)
        udt = np.sin(2.0*r-freq*(step+1))/(r+1.0)
        data = np.empty((n_samples,ndTot))
        data[:,0] = u.flatten() 
        data[:,1] = udt.flatten() 
    elif (args.problem_size=="medium"):
        #assert is_square(size) or size==1, "Number of MPI ranks must be square or 1"
        N = 256
        n_samples = N**2
        ndIn = 2
        ndTot = 4
        #x, y = partition_domain((-2*PI, 2*PI), (-2*PI, 2*PI), N, size, rank)
        partition = Partition(dimensions=2, comm=comm)
        part_origin = partition.origin
        part_extent = partition.extent
        x = np.linspace(part_origin[0],part_origin[0]+part_extent[0],num=N)*4*PI-2*PI
        y = np.linspace(part_origin[1],part_origin[1]+part_extent[1],num=N)*4*PI-2*PI
        x, y = np.meshgrid(x, y)
        coords = np.vstack((x.flatten(),y.flatten())).T
        r = np.sqrt(x**2+y**2)
        period = 100
        freq = 2*PI/period
        u = np.sin(2.0*r-freq*step)/(r+1.0)
        udt = np.sin(2.0*r-freq*(step+1))/(r+1.0)
        v = np.cos(2.0*r-freq*step)/(r+1.0)
        vdt = np.cos(2.0*r-freq*(step+1))/(r+1.0)
        data = np.empty((n_samples,ndTot))
        data[:,0] = u.flatten() 
        data[:,1] = v.flatten() 
        data[:,2] = udt.flatten() 
        data[:,3] = vdt.flatten() 
    elif (args.problem_size=="large"):
        N = 100
        n_samples = N**3
        ndIn = 3
        ndTot = 6
        partition = Partition(dimensions=3, comm=comm)
        part_origin = partition.origin
        part_extent = partition.extent
        x = np.linspace(part_origin[0],part_origin[0]+part_extent[0],num=N)*4*PI-2*PI
        y = np.linspace(part_origin[1],part_origin[1]+part_extent[1],num=N)*4*PI-2*PI
        z = np.linspace(part_origin[2],part_origin[2]+part_extent[2],num=N)*4*PI-2*PI
        x, y, z = np.meshgrid(x, y, z)
        coords = np.vstack((x.flatten(),y.flatten(),z.flatten())).T
        r = np.sqrt(x**2+y**2+z**2)
        period = 200
        freq = 2*PI/period
        u = np.sin(2.0*r-freq*step)/(r+1.0)
        udt = np.sin(2.0*r-freq*(step+1))/(r+1.0)
        v = np.cos(2.0*r-freq*step)/(r+1.0)
        vdt = np.cos(2.0*r-freq*(step+1))/(r+1.0)
        w = np.sin(2.0*r-freq*step)**2/(r+1.0)
        wdt = np.sin(2.0*r-freq*(step+1))**2/(r+1.0)
        data = np.empty((n_samples,ndTot))
        data[:,0] = u.flatten() 
        data[:,1] = v.flatten() 
        data[:,2] = w.flatten() 
        data[:,3] = udt.flatten() 
        data[:,4] = vdt.flatten() 
        data[:,5] = wdt.flatten() 
    elif (args.problem_size=="very_large"):
        N = 128
        n_samples = N**3
        ndIn = 3
        ndTot = 6
        partition = Partition(dimensions=3, comm=comm)
        part_origin = partition.origin
        part_extent = partition.extent
        x = np.linspace(part_origin[0],part_origin[0]+part_extent[0],num=N)*4*PI-2*PI
        y = np.linspace(part_origin[1],part_origin[1]+part_extent[1],num=N)*4*PI-2*PI
        z = np.linspace(part_origin[2],part_origin[2]+part_extent[2],num=N)*4*PI-2*PI
        x, y, z = np.meshgrid(x, y, z)
        coords = np.vstack((x.flatten(),y.flatten(),z.flatten())).T
        r = np.sqrt(x**2+y**2+z**2)
        period = 200
        freq = 2*PI/period
        u = np.sin(2.0*r-freq*step)/(r+1.0)
        udt = np.sin(2.0*r-freq*(step+1))/(r+1.0)
        v = np.cos(2.0*r-freq*step)/(r+1.0)
        vdt = np.cos(2.0*r-freq*(step+1))/(r+1.0)
        w = np.sin(2.0*r-freq*step)**2/(r+1.0)
        wdt = np.sin(2.0*r-freq*(step+1))**2/(r+1.0)
        data = np.empty((n_samples,ndTot))
        data[:,0] = u.flatten() 
        data[:,1] = v.flatten() 
        data[:,2] = w.flatten() 
        data[:,3] = udt.flatten() 
        data[:,4] = vdt.flatten() 
        data[:,5] = wdt.flatten() 

    return_dict = {
        "n_samples": n_samples,
        "n_dim_in": ndIn,
        "n_dim_tot": ndTot
    }
    return data, coords, return_dict

# Partition the global domain
def partition_domain(x_lim: Tuple[float,float], y_lim: Tuple[float,float],
                     N: int, comm_size: int, 
                     rank: int) -> Tuple[np.ndarray,np.ndarray]:
    if (comm_size==1):
        x = np.linspace(x_lim[0], x_lim[1], N)
        y = np.linspace(y_lim[0], y_lim[1], N)
    else:
        n_parts_per_dim = math.isqrt(comm_size)
        xrange = (x_lim[1]-x_lim[0])/n_parts_per_dim
        x_id = rank % n_parts_per_dim
        x_min = xrange*x_id
        x_max = xrange*(x_id+1)
        x = np.linspace(x_min, x_max, N)
        yrange = (y_lim[1]-y_lim[0])/n_parts_per_dim
        y_id = rank // n_parts_per_dim
        y_min = yrange*y_id
        y_max = yrange*(y_id+1)
        y = np.linspace(y_min, y_max, N)
    return x, y

# Print FOM
def print_fom(logger: logging.Logger, time2sol: float, train_data_sz: float, ssim_stats: dict) -> None:
    logger.info(f"Time to solution [s]: {time2sol:>.3f}")
    total_sr_time = ssim_stats["tot_meta"]["max"][0] \
                    + ssim_stats["tot_train"]["max"][0] \
                    + ssim_stats["tot_infer"]["max"][0]
    rel_sr_time = total_sr_time/time2sol*100
    rel_meta_time = ssim_stats["tot_meta"]["max"][0]/time2sol*100
    rel_train_time = ssim_stats["tot_train"]["max"][0]/time2sol*100
    rel_infer_time = ssim_stats["tot_infer"]["max"][0]/time2sol*100
    logger.info(f"Relative total overhead [%]: {rel_sr_time:>.3f}")
    logger.info(f"Relative meta data overhead [%]: {rel_meta_time:>.3f}")
    logger.info(f"Relative train overhead [%]: {rel_train_time:>.3f}")
    logger.info(f"Relative infer overhead [%]: {rel_infer_time:>.3f}")
    string = f": min = {train_data_sz/ssim_stats['train']['max'][0]:>4e} , " + \
             f"max = {train_data_sz/ssim_stats['train']['min'][0]:>4e} , " + \
             f"avg = {train_data_sz/ssim_stats['train']['avg']:>4e}"
    logger.info(f"Train data throughput [GB/s] " + string)

# MPI file handler for parallel logging
class MPIFileHandler(logging.FileHandler):                                      
    def __init__(self,
                 filename,
                 mode=MPI.MODE_WRONLY|MPI.MODE_CREATE|MPI.MODE_APPEND ,
                 encoding='utf-8',  
                 delay=False,
                 comm=MPI.COMM_WORLD ):                                                
        self.baseFilename = os.path.abspath('/'.join([os.getcwd(), filename]))                        
        self.mode = mode                                                        
        self.encoding = encoding                                            
        self.comm = comm                                                        
        if delay:                                                               
            #We don't open the stream, but we still need to call the            
            #Handler constructor to set level, formatter, lock etc.             
            logging.Handler.__init__(self)                                      
            self.stream = None                                                  
        else:                                                                   
           logging.StreamHandler.__init__(self, self._open())                   
                                                                                
    def _open(self):                                                            
        stream = MPI.File.Open( self.comm, self.baseFilename, self.mode )     
        stream.Set_atomicity(True)                                              
        return stream
                                                    
    def emit(self, record):
        """
        Emit a record.
        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        
        Modification:
            stream is MPI.File, so it must use `Write_shared` method rather
            than `write` method. And `Write_shared` method only accept 
            bytestring, so `encode` is used. `Write_shared` should be invoked
            only once in each all of this emit function to keep atomicity.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            stream.Write_shared((msg+self.terminator).encode(self.encoding))
            #self.flush()
        except Exception:
            self.handleError(record)
                                                         
    def close(self):
        if self.stream:                                                         
            self.stream.Sync()                                                  
            self.stream.Close()                                                 
            self.stream = None    
