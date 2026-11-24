from ase.build import bulk
from ase.calculators.espresso import Espresso, EspressoProfile
from ase.constraints import ExpCellFilter
from ase.optimize import LBFGS
from ase.io import read
import os

pseudo_path = os.path.expanduser('~/pseudos/SSSP_1.3.0_PBE_efficiency')

profile = EspressoProfile(
    command='/software/spackages_v0_21_prod/apps/linux-ubuntu22.04-zen2/gcc-13.2.0/quantum-espresso-7.2-x3achhjyz7nc3cpdwqvhwf7njqvidl5a/bin/pw.x',
    pseudo_dir=pseudo_path
)

pseudopotentials = {'Pb':' Pb.pbe-dn-kjpaw_psl.0.2.2.UPF',
                    'Ti': 'ti_pbe_v1.4.uspp.F.UPF',
                    'O': ' O.pbe-n-kjpaw_psl.0.1.UPF'}


input_data = {
    'calculation': 'scf',
    'restart_mode': 'from_scratch',
    'etot_conv_thr': 1e-5,
    'forc_conv_thr': 1e-4,
    'ecutwfc': 50,
    'ecutrho': 500,
    'input_dft': 'sla+pw+pbc+c09x',
    'conv_thr': 1e-12,
    'mixing_beta': 0.3,
    'diagonalization': 'david',
}


atoms = read('PbTiO3.cif')

calc = Espresso(profile=profile, pseudopotentials=pseudopotentials, tstress=True, tprnfor=True, kpts=(4, 4, 4), input_data=input_data)

atoms.calc = calc

filt = ExpCellFilter(atoms)
opt = LBFGS(filt, trajectory='opt.traj', logfile='opt.log')
opt.run(fmax=0.01)

# Extract optimized lattice vectors
optimized_cell = atoms.get_cell()

# Write to file
with open('lattice_parameter.txt', 'w') as f:
    f.write("Optimized Lattice Vectors (AA):\n")
    for vector in optimized_cell:
        f.write(f"{vector[0]:.6f} {vector[1]:.6f} {vector[2]:.6f}\n")
