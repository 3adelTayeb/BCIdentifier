# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 08:35:54 2023#

@author: Adel Tayeb
Application of the PSO to identify HTC Boundary Condition for a one thermal-Break 
Monoblock using MOOSE 
"""

from subprocess import call
import numpy as np
#import datetime
import os
import tkinter
#from tkinter import filedialog
import time
import multiprocessing
#from multiprocessing import Pool
import shutil
# Custom package from packages folder
#import packages.ansys_tools as ansys_tools
import packages.misc_tools as util


#%% Cost function including Force, strains and displacement for 2D measurement
def Cost_Fucn_ThermalBC(ARG1,ARG2,ARG3,ARG4,ARG5,ARG6,ARG7, fe_file_path, exp_data_path):
    # % Cost function calculation from experimental and FE data 
    # Setup up the root window of the GUI and hide it
    root = tkinter.Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()
    #% LOAD Exp DATA (in this case FE data)
    # Create FE data class to hold everything Exp data are FE data in this case 
    #Load thermocouple reading
    TC02_Exp = np.array(util.read_data_by_spec(os.path.join(exp_data_path, 'TC02.txt'),[1]*1,13))
    TC03_Exp = np.array(util.read_data_by_spec(os.path.join(exp_data_path, 'TC03.txt'),[1]*1,13))
    TC04_Exp = np.array(util.read_data_by_spec(os.path.join(exp_data_path, 'TC04.txt'),[1]*1,13))

    #% Launch Ansys simulation for the set of constitutive parameters 
    #fe_file_path = pwd + '\\FEData\\'
    file = os.path.join(fe_file_path, "Ansys_command.txt")
    with open(file, "w") as fid:
        fid.truncate()
        
    fid = open(file, 'w')
    fid.write(("ThermalBCOptimizer,{},{},{},{},{},{},{}").format(ARG1,ARG2,ARG3,ARG4,ARG5,ARG6,ARG7))
    fid.close()

    ansyscall = "C:\\Program Files\\ANSYS Inc\\v212\\ansys\\bin\\winx64\\MAPDL.exe"
    numprocessors = 1

    inputFile = os.path.join(fe_file_path, "Ansys_command.txt")

    # keep the standard ansys jobname
    jobname = "file"
    # make the output file be the input file plus timestamp
    outputFile = os.path.join(fe_file_path,
                                  jobname+
                                  ".out")
    callString = ("\"{}\" -p ansys -dis -mpi INTELMPI"
                  " -np {} -dir \"{}\" -j \"{}\" -s read"
                  " -b -i \"{}\" -o \"{}\"").format(
                          ansyscall,
                          numprocessors,
                          fe_file_path,
                          jobname,
                          inputFile,
                          outputFile)
    # tic = time.time()
    call(callString,shell=False)
    # toc = time.time()
    # print('Simulation took {:.4f} seconds'.format(toc-tic))
    TC02_FE = np.array(util.read_data_by_spec(os.path.join(fe_file_path, 'TC02.txt'),[1]*2,13))
    TC03_FE = np.array(util.read_data_by_spec(os.path.join(fe_file_path, 'TC03.txt'),[1]*2,13))
    TC04_FE = np.array(util.read_data_by_spec(os.path.join(fe_file_path, 'TC04.txt'),[1]*2,13))
    # computing the cost function as the squared error of force and strains
    # Initializing the cost function
    Cf_Temp =  abs((np.average(TC02_FE[:,1])-TC02_Exp[0])) + abs((np.average(TC03_FE[:,1])-TC03_Exp[0])) + abs((np.average(TC04_FE[:,1])-TC04_Exp[0]))
    return Cf_Temp
#%% Initialization and creation of all the directories for parallel simulations 
numWorkers = int(multiprocessing.cpu_count()/2)

# Setup up the root window of the GUI and hide it
root = tkinter.Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()
# Gets the directory for the main input file 
cwd = os.getcwd()+'\\'
# Gets the directory of the experimental results (change accordingly)
exp_data_path = os.getcwd()+'\\TestData\\'
tempPath = os.path.join(cwd, 'Ansys_Data_Temp\\')
#print('Creating {} temporary directories for running ANSYS in parallel'.format(numWorkers))
outputPaths = []
modelFullPaths = []
modelFile = 'ThermalBCOptimizer.mac'
modelCommand = 'Ansys_command.txt'
MatParam = 'ITER_DEFPROPS.mlib'
HHFDist = 'HHFDist.csv'
HHFFace = 'HHFFace.csv'

# list containing the same exp data path the number of workers times (for the Cost function routine call) 
exp_data_Paths = []
for i in range(numWorkers):
    exp_data_Paths.append(exp_data_path)
#%% PSO-Based FEMU in parallel INITIALIZATION and PARAMETERS
# Setting the Global optimisation parameters and hyperparameters of PSO
# PSO Hyperparameters
omega = 1.2; c1 = 2; c2 =2;
it_max = 100; nb_part = numWorkers; 
trace_glob = np.zeros((it_max+1, 1)) # best value of objective function each iteration
#fitness = np.zeros((1, nb_part)) # value of the objective function for all particle each iteration
delta_omega= (omega-0.4)/it_max;
delta_c1= c1/it_max;
delta_c2= c2/it_max;
epsilon_PSO = 1E-5 # minimum value for the objective function 
prob_dim = 7 # problem dimension i.e. number of variables to be identified 
# Research domain for the variables to be identified defined by upper and lower bounds
X_min = np.array([[48.3E3], [55.85E3], [63.13E3], [69.68E3],[74.24E3],[0.5],[0.5]])
X_max = np.array([[72.45E3], [83.78E3], [94.699E3], [104.52E3],[111.36E3],[3],[3]])
# corresponding Velocity domain
V_min = np.zeros((prob_dim, 1))
for i in range(0, prob_dim):
    V_min[i, 0] = -(X_max[i, 0]-X_min[i, 0])/5

V_max = -V_min

# Initializing the velocities 
velocities = np.zeros((prob_dim,nb_part));
for j in range(0, nb_part):
    for i in range(0, prob_dim):
        velocities[i, j]=np.random.rand()*(V_max[i, 0]-V_min[i, 0])+V_min[i, 0]

# Initializing the best value of the objective function of each particle 
P_best = np.zeros((nb_part, 1))
P_best[:, 0]=10e10
# best position of each particle in the solution space
best_perso=np.zeros((prob_dim,nb_part))
# Initializing the best global particle in terms of cost function
G_best = 10e10
# best particle in the swarm in terms of the identified parameters
best_glob = np.zeros((prob_dim, 1))
target = np.zeros((nb_part, 1))
# matrix is the matrix containing the optimisation variables i.e. constitutive  
# parameters of each particle at each iteration 
matrix = np.zeros((prob_dim,nb_part))
for i in range(0, prob_dim):
    for j in range(0, nb_part):
        matrix[i, j]=(X_max[i, 0]-X_min[i, 0])*np.random.rand()+X_min[i, 0]
        
iteration_PSO = 0 # initialiazing the number of iterations
iteration_convergence = 1 # number of iteration to consider convergence if the 
# difference between two consecutive objective functions does not exceed Epsilon
# this is the initialisation and if this condition is satisfied then 
#  iteration_convergence = iteration_convergence +1

#%% PSO LOOP
Cf_tot = np.zeros((numWorkers, 1))
# The parallel call part starts here
if __name__ == '__main__':
    tic = time.time()
    outputPaths = []
    modelFullPaths = []
    for ww in range(0, numWorkers):      
         outputPaths.append(os.path.join(tempPath, 'ANSYSTemp_{}\\'.format(ww)))
         if os.path.isdir(outputPaths[ww]):
             shutil.rmtree(outputPaths[ww], ignore_errors=False, onerror=None)
         os.mkdir(outputPaths[ww])
         shutil.copy(modelFile, outputPaths[ww])
         shutil.copy(modelCommand, outputPaths[ww])
         shutil.copy(MatParam, outputPaths[ww])
         shutil.copy(HHFDist, outputPaths[ww])
         shutil.copy(HHFFace, outputPaths[ww])
         modelFullPaths.append(os.path.join(outputPaths[ww], modelCommand))
    while (iteration_PSO<=it_max) and (iteration_convergence<=30):
        # ctx = .get_context("spawn")
        with multiprocessing.Pool(16) as pool:
            tasks = [*zip(matrix[0,:], matrix[1,:], matrix[2,:], matrix[3,:], matrix[4,:], matrix[5,:], matrix[6,:], outputPaths, exp_data_Paths)]
            Cf_tot = pool.starmap(Cost_Fucn_ThermalBC, iterable=tasks)
        fitness = np.array(Cf_tot)
        fitness = fitness[:, 0]
        print('this is the fitness: ', fitness)
        # definition of the stationary vector of Markov chain
        best = min(fitness)
        # Initialiazing the PageRank vector i.e. target
        for i in range(0, nb_part):
            target[i] = best*100/fitness[i]
        target = target/sum(target)
        # determining the topology of the population
        # Subroutine enabling the computation of the transition matrix once the 
        # stationary markov chain vector is known
        epsilon = 1e-3
        # Generalizing the first connectivity matrix
        matrice = np.random.rand(nb_part, nb_part)
        for i in range(0, nb_part):
            somme = sum(matrice[i, :])
            matrice[i, :] = matrice[i, :]/somme
        # Determining the incrementation value delta
        a = min(target)
        ordre = 0
        while a < 1:
            a = a * 10
            ordre = ordre +1
        delta = 1*10**(-ordre)
        # computing the first residual
        I = np.eye(nb_part)
        PageRank = np.zeros((1, nb_part))
        PageRank[:, 0] = 1/nb_part
        residu = np.zeros((1, target.shape[0]))
        # Computing the residual
        norme = 1
        iteration = 1 
        iteration_max = 600
        while (norme >= epsilon) and (iteration <= iteration_max):
            R_max = residu[0, 0]
            R_min = residu[0, 0]
            col_max = 0
            col_min = 0
            for i in range(0, residu.shape[0]):
                if(R_max < residu[0, i]):
                    R_max = residu[0, i]
                    col_max = i
                if(R_min > residu[0, i]) :
                    R_min =  residu[0, i]
                    col_min = i
            # random choice of a matrix line
            ligne = round(nb_part*np.random.rand())
            while ligne == nb_part:
                ligne = round(nb_part*np.random.rand())
                
            if (matrice[ligne, col_max]-delta<0) or (matrice[ligne, col_min]+delta<0):
                ligne = round(nb_part*np.random.rand())
                if ligne == nb_part:
                    while ligne == nb_part:
                        ligne = round(nb_part*np.random.rand())
            matrice[ligne, col_max] = matrice[ligne,col_max]-delta
            matrice[ligne, col_min] = matrice[ligne,col_min]+delta
            
                
            # Computing the PageRank
            residual = 1
            k = 0
            pi = PageRank
            while residual >= epsilon:
                prevpi = pi
                k = k+1
                pi = np.dot(pi, matrice)
                residual = np.linalg.norm(pi - prevpi, 1)
                
            PageRank = pi
            # Computing the new residual
            residu = target - PageRank
            # Norm of the residual
            norme = np.linalg.norm(residu)
            iteration = iteration +1
            # Getting the best particle for the whole swarm
        for i in range(0, nb_part):
            if fitness[i] < P_best[i, 0] :
                P_best[i, 0] = fitness[i]
                best_perso[:, i] = matrix[:, i]
        # Getting the best particle for the whole swarm
        F_min = fitness[0]
        if fitness.min() < G_best:
            for i in range(0, fitness.shape[0]):
                if (F_min >= fitness[i]) :
                    F_min =  fitness[i]
                    index = i
            G_best = fitness.min()
            best_glob[:, 0] = matrix[:, index]
            trace_glob[iteration_PSO] = fitness.min()
        else:
            trace_glob[iteration_PSO] = trace_glob[iteration_PSO-1]
        # Verification if we can stop the optimisation
        if iteration_PSO !=0:
            if abs(trace_glob[iteration_PSO]-trace_glob[iteration_PSO-1]) <= epsilon_PSO:
                iteration_convergence = iteration_convergence + 1
            else:
                iteration_convergence = 0
        # Write the results if needed

        # Computing the new velocities of particles 
        for i in range(0, nb_part):
            r1 = np.random.rand()
            r2 = np.random.rand()
            velocities[:, i] = omega*velocities[:, i] + c1*r1*(best_perso[:, i]-matrix[:, i])
            somme = 0
            for j in range(0, nb_part):
                somme = somme + matrice[i, j]*(best_perso[:, j]-matrix[:, i])
            velocities[:, i] = velocities[:, i] + c2*r2*somme
        
            for j in range(0, prob_dim):
                if velocities[j, i] < V_min[j, 0]:
                     velocities[j, i] = V_min[j, 0]
                elif velocities[j, i] > V_max[j, 0]:
                    velocities[j, i] = V_max[j, 0]
         # Computing new positions of all particles 
        for j in range(0, nb_part):
            for i in range(0, prob_dim):
                matrix[i, j] = matrix[i, j] + velocities[i, j]
                if matrix[i, j] < X_min[i, 0]:
                    matrix[i, j] = X_min[i, 0]
                elif velocities[i, j] > X_max[i, 0]:
                    velocities[i, j] = X_max[i, 0]

        iteration_PSO = iteration_PSO + 1
        omega = omega -delta_omega
        c1 = c1 - delta_c1
        c2 = c2 -delta_c2
    toc = time.time()
    print('PSO-Based FEMU took {:.4f} seconds'.format(toc-tic))

    
    
