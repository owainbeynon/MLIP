from ase import units
from ase.md.langevin import Langevin
from ase.io import read, write
import numpy as np
import time
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from mace.calculators import MACECalculator
from ase.build.supercells import make_supercell

calculator = MACECalculator(model_paths='../../model/MACE_C09x-PBEc_QE.model', device='cuda')
init_conf = read('opt_cub.cif', '0')

init_conf.set_calculator(calculator)

MaxwellBoltzmannDistribution(init_conf, temperature_K=300)

dyn = Langevin(init_conf, 1*units.fs, temperature_K=300, friction=0.02, logfile="NVT_cub.log", trajectory="NVT_cub.traj")

dyn.run(2500)
print("MD finished!")