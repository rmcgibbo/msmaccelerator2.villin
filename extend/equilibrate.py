import numpy as np
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *

###########################
temperature = 300*kelvin
timestep = 1.0*femtosecond
n_steps = int(100*picoseconds / timestep)
report_interval = int(1*picoseconds / timestep)
###########################

pdb = PDBFile('minimized.pdb')
pdb.topology.loadBondDefinitions('../residues-nle.xml')
pdb.topology.createStandardBonds()
forcefield = ForceField('amber99sbildn.xml', '../amber99sbildn-nle.xml',
                        'tip3p.xml')
system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
                                 constraints=HBonds, rigidWater=False,
                                 nonbondedCutoff=0.8*nanometers)
integrator = LangevinIntegrator(temperature, 1.0/picosecond, timestep)
integrator.setConstraintTolerance(0.00001)

simulation = Simulation(pdb.topology, system, integrator)
simulation.context.setPositions(pdb.positions)
simulation.context.setVelocitiesToTemperature(temperature)

state = simulation.context.getState(getPositions=True, getVelocities=True, getForces=True, getEnergy=True,
                                    getParameters=True, enforcePeriodicBox=True)

print 'Initial state'
print 'Kinetic Energy', state.getKineticEnergy()
print 'RMS Velocity', np.sqrt(np.mean((np.square(state.getVelocities()))))

simulation.reporters.append(StateDataReporter(sys.stdout, report_interval, time=True, step=True,
                                              temperature=True, kineticEnergy=True, potentialEnergy=True))
simulation.reporters.append(DCDReporter('equilibration2.dcd', report_interval))

print 'total n_steps. starting.'
simulation.step(n_steps)
