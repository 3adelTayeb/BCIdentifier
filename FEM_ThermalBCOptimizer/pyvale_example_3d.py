'''
================================================================================
Example: 3d thermocouples on a monoblock

pyvale: the python validation engine
License: MIT
Copyright (C) 2024 The Computer Aided Validation Team
================================================================================
'''
from pathlib import Path
import matplotlib.pyplot as plt
import mooseherder as mh
import pyvale
import numpy as np
from numpy import linalg as LA
import os


def main() -> None:
    """pyvale example:
    """
    data_path = Path('case18/case18-mod-vars_out.e')
    data_reader = mh.ExodusReader(data_path)
    sim_data = data_reader.read_all_sim_data()
    field_name = list(sim_data.node_vars.keys())[0] # type: ignore
    # Scale to mm to make 3D visualisation scaling easier
    sim_data.coords = sim_data.coords*1000.0 # type: ignore
    heatFlux = 5e6*(1-np.exp(-100*sim_data.time))

    print(heatFlux)

    exp_path = Path('TestData')

    tc02_exp = np.loadtxt((exp_path / 'TC02.csv'), delimiter=',')
    tc03_exp = np.loadtxt((exp_path / 'TC03.csv'), delimiter=',')
    tc04_exp = np.loadtxt((exp_path / 'TC04.csv'), delimiter=',')

    
    sample_time = np.hstack((tc02_exp[tc02_exp[:,0]< max(sim_data.time), 0], 30))
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
    obj_func = (LA.norm(tc02-measurements[0,0,:])+
                LA.norm(tc03-measurements[1,0,:])+
                LA.norm(tc04-measurements[2,0,:]))/3
    print('The total cost function is\n', obj_func)
    print(os.cpu_count())



    # pv_plot = pyvale.plot_sensors_on_sim(tc_array,field_name)

    # # Set this to 'interactive' to get an interactive 3D plot of the simulation
    # # and labelled sensor locations, set to 'save_fig' to create a vector
    # # graphic using a specified camera position.
    # pv_plot_mode = 'interactive'

    # if pv_plot_mode == 'interactive':
    #     pv_plot.camera_position = [(52.198, 26.042, 60.099),
    #                                 (0.0, 4.0, 5.5),
    #                                 (-0.190, 0.960, -0.206)]
    #     pv_plot.show()
    #     print('Camera positions = ')
    #     print(pv_plot.camera_position)
    # if pv_plot_mode == 'save_fig':
    #     # Determined manually by moving camera and then dumping camera position
    #     # to console after window close - see 'interactive above'
    #     pv_plot.camera_position = [(52.198, 26.042, 60.099),
    #                                 (0.0, 4.0, 5.5),
    #                                 (-0.190, 0.960, -0.206)]
    #     save_render = Path('src/examples/monoblock_thermal_sim_view.svg')
    #     pv_plot.save_graphic(save_render) # only for .svg .eps .ps .pdf .tex
    #     pv_plot.screenshot(save_render.with_suffix('.png'))

    # Set this to 'interactive' to get a matplotlib.pyplot with the sensor
    # traces plotted over time. Set to 'save_fig' to save an image of the plot
    # to file.
    trace_plot_mode = 'interactive'

    (fig,_) = pyvale.plot_time_traces(tc_array,field_name)

    if trace_plot_mode == 'interactive':
        plt.show()
    if trace_plot_mode == 'save_fig':
        save_traces = Path('src/examples/monoblock_thermal_traces.png')
        fig.savefig(save_traces, dpi=300, format='png', bbox_inches='tight')


if __name__ == '__main__':
    main()