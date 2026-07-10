from ase.io import read, write
from mace.calculators import MACECalculator
from ase.optimize.bfgs import BFGS
from ase.filters import ExpCellFilter

# Initialize calculator
calculator = MACECalculator(model_paths='../../model/MACE_C09x-PBEc_QE.model', device='cuda')
init_conf = read('PTO_tet.cif', '0')
init_conf.set_calculator(calculator)

# Apply cell filter for optimization
cell = ExpCellFilter(init_conf)

# Run optimization
opt = BFGS(cell, logfile='opt_tet.log', trajectory='opt_tet.traj')
opt.run(fmax=0.01)

# Extract optimized lattice vectors
optimized_cell = init_conf.get_cell()

# Write to file
with open('lattice_parameter_tet.txt', 'w') as f:
    f.write("Optimized Lattice Vectors (AA):\n")
    for vector in optimized_cell:
        f.write(f"{vector[0]:.6f} {vector[1]:.6f} {vector[2]:.6f}\n")

print("Lattice parameters saved to lattice_parameter.txt")
