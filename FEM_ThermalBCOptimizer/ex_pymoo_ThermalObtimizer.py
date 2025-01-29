# EXAMPLE: pymoo optimisation
import numpy as np
import matplotlib.pyplot as plt

from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination.default import DefaultSingleObjectiveTermination
from pymoo.optimize import minimize
import time
from pathlib import Path
from mooseherder import (MooseConfig,
                         MooseRunner,
                         GmshRunner,
                         InputModifier)
import matplotlib.pyplot as plt
import mooseherder as mh
import pyvale
import numpy as np
from numpy import linalg as LA

#from pyvale.visualisation.plotopts import GeneralPlotOpts
#import pyvale.optimisers.checkfuncs as cf

#-------------------------------------------------------------------------------
#======================================
# Change this to run a different case
CASE_STR = 'case18'
#======================================

CASE_FILES = (CASE_STR+'.geo',CASE_STR+'.i')

CASE_DIR = Path(CASE_STR+'/')


USER_DIR = Path.home()

FORCE_GMSH = False

def cost_func(x):
        # NOTE: if the msh file exists then gmsh will not run
    if (((CASE_DIR / CASE_FILES[0]).is_file() and not
        (CASE_DIR / CASE_FILES[0]).with_suffix('.msh').is_file()) or
        FORCE_GMSH):
        gmsh_runner = GmshRunner(USER_DIR / 'gmsh/bin/gmsh')

        gmsh_start = time.perf_counter()
        gmsh_runner.run(CASE_DIR / CASE_FILES[0])
        gmsh_run_time = time.perf_counter()-gmsh_start
    else:
        #print('Bypassing gmsh.')
        gmsh_run_time = 0.0

    config = {'main_path': USER_DIR / 'moose',
            'app_path': USER_DIR / 'proteus',
            'app_name': 'proteus-opt'}

    moose_config = MooseConfig(config)
    moose_runner = MooseRunner(moose_config)

    moose_runner.set_run_opts(n_tasks = 8,
                              n_threads = 1,
                              redirect_out = True)
    moose_mod = InputModifier(CASE_DIR / CASE_FILES[1], comment_char="#", end_char="")

    # print("Variables found the top of the MOOSE input file:")
    # print(moose_mod.get_vars())
    # print()

    new_vars = {"Arg1": x[0], "Arg2": x[1], "Arg3": x[2], "Arg4": x[3], "Arg5": x[4], "surfHeatFlux": x[5]}
    moose_mod.update_vars(new_vars)

    # print("New variables inserted:")
    # print(moose_mod.get_vars())
    # print()

    moose_save = Path(CASE_DIR / "case18-mod-vars.i")
    moose_mod.write_file(moose_save)

    # print("Modified input script written to:")
    # print(moose_save)
    moose_start_time = time.perf_counter()
    moose_runner.run(CASE_DIR / "case18-mod-vars.i")
    moose_run_time = time.perf_counter() - moose_start_time

    # print()
    # print("="*80)
    # print(f'Gmsh run time = {gmsh_run_time:.2f} seconds')
    # print(f'MOOSE run time = {moose_run_time:.3f} seconds')
    # print("="*80)
    # print()
    data_path = Path('case18/case18-mod-vars_out.e')
    data_reader = mh.ExodusReader(data_path)
    sim_data = data_reader.read_all_sim_data()
    field_name = list(sim_data.node_vars.keys())[0] # type: ignore
    # Scale to mm to make 3D visualisation scaling easier
    sim_data.coords = sim_data.coords*1000.0 # type: ignore

    exp_path = Path('TestData')

    tc02_exp = np.loadtxt((exp_path / 'TC02.csv'), delimiter=',')
    tc03_exp = np.loadtxt((exp_path / 'TC03.csv'), delimiter=',')
    tc04_exp = np.loadtxt((exp_path / 'TC04.csv'), delimiter=',')

    
    sample_time = np.hstack((tc02_exp[tc02_exp[:,0]< max(sim_data.time), 0], max(sim_data.time)))
    # heatFlux = 5e6*(1-np.exp(-100*sim_data.time))

    # plt.plot(sim_data.time,heatFlux, '-or')
    # plt.show()
    tc02 = np.interp(sample_time, tc02_exp[:,0], tc02_exp[:,1])
    tc03 = np.interp(sample_time, tc03_exp[:,0], tc03_exp[:,1])
    tc04 = np.interp(sample_time, tc04_exp[:,0], tc04_exp[:,1])
 
    sens_pos = np.array([[12.5, 25.34, 4.3], 
                         [12.5, 16.86, 8.31],
                         [12.5, 3.77, 7.66]])
    # pyvale.create_sensor_pos_array(n_sens,x_lims,y_lims,z_lims)
    

    descriptor = pyvale.SensorDescriptorFactory.temperature_descriptor()

    t_field = pyvale.ScalarField(sim_data,field_name,spat_dim=3)

    tc_array = pyvale.PointSensorArray(sens_pos,
                                    t_field,
                                    sample_time,
                                    descriptor)
    
    measurements = tc_array.get_truth_values()
    # print(measurements[0,0,:])
    cost = (LA.norm(tc02-measurements[0,0,:],1)+
                LA.norm(tc03-measurements[1,0,:],1)+
                LA.norm(tc04-measurements[2,0,:],1))/(3*sample_time.shape[0])
    return np.array(cost)

class TestProblem(Problem):
    def __init__(self, n_var=6, xl= [45.5e3, 56.92e3, 68.34e3, 79.76e3, 90.03e3, 3e6],
                  xu= [68.26e3, 85.39e3, 102.51e3, 119.64e3, 135.05e3, 8e6]):
        super().__init__(n_var=n_var, n_obj=1, xl=xl, xu=xu, vtype=float)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = np.apply_along_axis(cost_func, axis=1, arr=x)

#-------------------------------------------------------------------------------
def main() -> None:
    xl = [45.5e3, 56.92e3, 68.34e3, 79.76e3, 90.03e3, 3e6]
    xu = [68.26e3, 85.39e3, 102.51e3, 119.64e3, 135.05e3, 8e6]
    problem = TestProblem(xl=xl,xu=xu)

    alg = 'PSO'
    if alg == 'PSO':
        algorithm = PSO(pop_size=8)
    else:
        algorithm = GA(
            pop_size=8,
            eliminate_duplicates=True)

    termination = DefaultSingleObjectiveTermination(
        xtol=1e-8,
        cvtol=1e-6,
        ftol=1e-3,
        period=10, # Number of generations that need to be below tols
        n_max_gen=25,
        n_max_evals=100000)

    res = minimize(problem,
                algorithm,
                termination,
                seed=1,
                verbose=True)

    print(80*'=')
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    print(80*'=')

    # pp = GeneralPlotOpts()
    # (fig,ax) = cf.plot_fun_2d(f'Min with {alg}',
    #                           cost_func,(xl,xu),(xl,xu),100)
    # plt.plot(res.X[0],res.X[1],'+r',lw=pp.lw,ms=pp.ms)
    # plt.show()
# x = np.array([[45.5e3, 56.92e3, 68.34e3, 79.76e3, 90.03e3, 3e6]])
# print(type(cost_func(x)))
if __name__ == "__main__":
    main()
