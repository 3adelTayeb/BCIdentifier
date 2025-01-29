# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 10:30:46 2023

@author: Adel Tayeb
"""
import numpy as np
#import datetime
from subprocess import call
import os
import tkinter
#from tkinter import filedialog
#import time
#import multiprocessing
#from multiprocessing import Pool
#import shutil
# Custom package from packages folder
#import packages.ansys_tools as ansys_tools
import packages.misc_tools as util
# % Cost function calculation from experimental and FE data 
# Setup up the root window of the GUI and hide it
root = tkinter.Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()

cwd = os.getcwd()+'\\'

exp_data_path = os.getcwd()+'\\TestData\\'
#tempPath = os.path.join(cwd, 'Ansys_Data_Temp\\')

ARG1 = 53.83e3
ARG2 = 78.84e3
ARG3 = 92.1e3
ARG4 = 90.37e3
ARG5 =100.57e3
ARG6 = 2.49
ARG7 = 0.958
#Load thermocouple reading
TC02_Exp = np.array(util.read_data_by_spec(os.path.join(exp_data_path, 'TC02.txt'),[1]*1,13))
TC03_Exp = np.array(util.read_data_by_spec(os.path.join(exp_data_path, 'TC03.txt'),[1]*1,13))
TC04_Exp = np.array(util.read_data_by_spec(os.path.join(exp_data_path, 'TC04.txt'),[1]*1,13))


#% Launch Ansys simulation for the set of constitutive parameters 
fe_file_path = cwd + 'FEData\\'
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
Cf_Temp = abs((np.average(TC02_FE[:,1])-TC02_Exp[0])/TC02_Exp[0])**2 + abs((np.average(TC03_FE[:,1])-TC03_Exp[0])/TC03_Exp[0])**2 + abs((np.average(TC04_FE[:,1])-TC04_Exp[0])/TC04_Exp[0])**2
print('Obj Funcion: ', Cf_Temp)
print('Temp diff TC02: ', abs(np.average(TC02_FE[:,1])-TC02_Exp[0]))
print('Temp diff TC03:  ', abs(np.average(TC03_FE[:,1])-TC03_Exp[0]))
print('Temp diff TC04:  ', abs(np.average(TC04_FE[:,1])-TC04_Exp[0]))
print('Temp of TC02 is: ', abs(np.average(TC02_FE[:,1])))
print('Temp of TC03 is:  ', abs(np.average(TC03_FE[:,1])))
print('Temp of TC04 is:  ', abs(np.average(TC04_FE[:,1])))
          
          




