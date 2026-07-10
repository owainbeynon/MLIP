from ase.atoms import Atoms
from ase.constraints import FixSymmetry
from ase.io import read
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from mace.calculators import MACECalculator 
from ase.optimize import BFGS
from ase.filters import ExpCellFilter

calculator = MACECalculator(model_paths='../../model/MACE_C09x-PBEc_QE.model', device='cuda')

atoms = read("opt_tet.cif")
atoms.set_calculator(calc=calculator)

atoms.set_constraint(FixSymmetry(atoms))
opt_structure = ExpCellFilter(atoms)
opt = BFGS(opt_structure)
opt.run(fmax=0.001)



phnpy_struct = PhonopyAtoms(
    symbols=atoms.get_chemical_symbols(),
    positions=atoms.get_positions(),
    cell=atoms.get_cell(),
    masses=atoms.get_masses(),
)

def calculate_plot_phonons(d=0.01,n=3):
    phonons = Phonopy(
        phnpy_struct,
        supercell_matrix=[[n, 0, 0],
                          [0, n, 0],
                          [0, 0, n]],
    )

    phonons.generate_displacements(distance=d)
    sets_of_forces = []
    supercells = phonons.supercells_with_displacements

    for d in supercells:
        # Convert back to ASE
        d_ase = Atoms(symbols=d.symbols,
                      positions=d.positions,
                      cell=d.cell,
                      pbc=True)
        d_ase.set_calculator(calculator)
        forces = d_ase.get_forces()
        sets_of_forces.append(forces)

    phonons.forces = sets_of_forces
    phonons.produce_force_constants()
    phonons.save()
    phonons.auto_band_structure(npoints=100, plot=True, write_yaml=True, with_eigenvectors=True).savefig("band_tet.png")

calculate_plot_phonons()

