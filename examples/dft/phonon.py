from ase.atoms import Atoms
from ase.optimize import BFGS
from ase.constraints import FixSymmetry
from ase.io import read
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from ase.calculators.espresso import Espresso, EspressoProfile
import os

pseudo_path = os.path.expanduser('~/pseudos/SSSP_1.3.0_PBE_efficiency')

profile = EspressoProfile(
    command='/software/spackages_v0_21_prod/apps/linux-ubuntu22.04-zen2/gcc-13.2.0/quantum-espresso-7.2-x3achhjyz7nc3cpdwqvhwf7njqvidl5a/bin/pw.x',
    pseudo_dir=pseudo_path
)

pseudopotentials = {
    'Pb': 'Pb.pbe-dn-kjpaw_psl.0.2.2.UPF',
    'Ti': 'ti_pbe_v1.4.uspp.F.UPF',
    'O': 'O.pbe-n-kjpaw_psl.0.1.UPF'
}

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
    'diagonalization': 'david'
}

calc = Espresso(
    profile=profile, 
    pseudopotentials=pseudopotentials, 
    tstress=True, 
    tprnfor=True, 
    kpts=(4, 4, 4), 
    input_data=input_data
)

atoms = read("pbe_c09_tetragonal.xyz")
atoms.calc = calc

atoms.set_constraint(FixSymmetry(atoms))
opt = BFGS(atoms)
opt.run(fmax=0.001)

# FIX 1: 'atoms' is already an ASE Atoms object after BFGS optimization
structure = atoms

phnpy_struct = PhonopyAtoms(
    symbols=structure.get_chemical_symbols(),
    positions=structure.get_positions(),
    cell=structure.get_cell(),
    masses=structure.get_masses(),
)

def calculate_plot_phonons(d=0.01, n=3):
    phonons = Phonopy(
        phnpy_struct,
        supercell_matrix=[[n, 0, 0],
                         [0, n, 0],
                         [0, 0, n]],
    )
    phonons.generate_displacements(distance=d)
    sets_of_forces = []
    supercells = phonons.get_supercells_with_displacements()

    # Renamed loop variable to 'sc' to avoid shadowing function argument 'd'
    for sc in supercells:
        d_ase = Atoms(
            symbols=sc.get_chemical_symbols(),
            positions=sc.get_positions(),
            cell=sc.get_cell(),
            pbc=True
        )
        d_ase.set_calculator(calc)
        forces = d_ase.get_forces()
        sets_of_forces.append(forces)

    phonons.forces = sets_of_forces
    phonons.produce_force_constants()
    phonons.save(settings={'force_constants': True})
    phonons.auto_band_structure(npoints=100, plot=True, write_yaml=True).savefig("bandstructure.png")

# FIX 2: Invoke the function to run the phonon workflow on the optimized structure
calculate_plot_phonons(d=0.01, n=3)
