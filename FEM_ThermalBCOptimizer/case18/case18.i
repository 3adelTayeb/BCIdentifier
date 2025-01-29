#-------------------------------------------------------------------------
# pyvale: gmsh,monoblock,3mat,thermal,steady,
#-------------------------------------------------------------------------

orderString=FIRST

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loads and BCs
stressFreeTemp=20   # degC
coolantTemp=150     # degC

end_time = 30
# time_step = 0.5

# mesh file
# Mesh file string
mesh_file = 'case18.msh'
#-------------------------------------------------------------------------
#_* MOOSEHERDER VARIABLES - START

Arg1 = 54.59e3
Arg2 = 84.33e3
Arg3 = 102.5e3
Arg4 = 119.51e3
Arg5 = 101.06e3
surfHeatFlux= 5.711e6   # W/m^2

#** MOOSEHERDER VARIABLES - END
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------


[Mesh]
  type = FileMesh
  file = ${mesh_file}
[]

[Variables]
  [temperature]
    family = LAGRANGE
    order = ${orderString}
    initial_condition = ${coolantTemp}
  []
[]

[Kernels]
  [heat_conduction]
    type = HeatConduction
    variable = temperature
  []
  [time_derivative]
    type = HeatConductionTimeDerivative
    variable = temperature
  []
  [heat_capacity_derivative]
    type = SpecificHeatConductionTimeDerivative
    variable = temperature
  []
[]

[Functions]
  [cucrzr_thermal_expansion]
    type = PiecewiseLinear
    xy_data = '
      20 1.67e-05
      50 1.7e-05
      100 1.73e-05
      150 1.75e-05
      200 1.77e-05
      250 1.78e-05
      300 1.8e-05
      350 1.8e-05
      400 1.81e-05
      450 1.82e-05
      500 1.84e-05
      550 1.85e-05
      600 1.86e-05
    '
  []
  [copper_thermal_expansion]
    type = PiecewiseLinear
    xy_data = '
      20 1.67e-05
      50 1.7e-05
      100 1.72e-05
      150 1.75e-05
      200 1.77e-05
      250 1.78e-05
      300 1.8e-05
      350 1.81e-05
      400 1.82e-05
      450 1.84e-05
      500 1.85e-05
      550 1.87e-05
      600 1.88e-05
      650 1.9e-05
      700 1.91e-05
      750 1.93e-05
      800 1.96e-05
      850 1.98e-05
      900 2.01e-05
    '
  []
  [tungsten_thermal_expansion]
    type = PiecewiseLinear
    xy_data = '
      20 4.5e-06
      100 4.5e-06
      200 4.53e-06
      300 4.58e-06
      400 4.63e-06
      500 4.68e-06
      600 4.72e-06
      700 4.76e-06
      800 4.81e-06
      900 4.85e-06
      1000 4.89e-06
      1200 4.98e-06
      1400 5.08e-06
      1600 5.18e-06
      1800 5.3e-06
      2000 5.43e-06
      2200 5.57e-06
      2400 5.74e-06
      2600 5.93e-06
      2800 6.15e-06
      3000 6.4e-06
      3200 6.67e-06
    '
  []
[]

[Materials]
  [cucrzr_thermal_conductivity]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 318
      50 324
      100 333
      150 339
      200 343
      250 345
      300 346
      350 347
      400 347
      450 346
      500 346
    '
    variable = temperature
    property = thermal_conductivity
    block = 'pipe-cucrzr'
  []
  [copper_thermal_conductivity]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 401
      50 398
      100 395
      150 391
      200 388
      250 384
      300 381
      350 378
      400 374
      450 371
      500 367
      550 364
      600 360
      650 357
      700 354
      750 350
      800 347
      850 344
      900 340
      950 337
      1000 334
    '
    variable = temperature
    property = thermal_conductivity
    block = 'interlayer-cu'
  []
  [tungsten_thermal_conductivity]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 173
      50 170
      100 165
      150 160
      200 156
      250 151
      300 147
      350 143
      400 140
      450 136
      500 133
      550 130
      600 127
      650 125
      700 122
      750 120
      800 118
      850 116
      900 114
      950 112
      1000 110
      1100 108
      1200 105
    '
    variable = temperature
    property = thermal_conductivity
    block = 'armour-w'
  []

  [cucrzr_density]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 8900
      50 8886
      100 8863
      150 8840
      200 8816
      250 8791
      300 8797
      350 8742
      400 8716
      450 8691
      500 8665
    '
    variable = temperature
    property = density
    block = 'pipe-cucrzr'
  []
  [copper_density]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 8940
      50 8926
      100 8903
      150 8879
      200 8854
      250 8829
      300 8802
      350 8774
      400 8744
      450 8713
      500 8681
      550 8647
      600 8612
      650 8575
      700 8536
      750 8495
      800 8453
      850 8409
      900 8363
    '
    variable = temperature
    property = density
    block = 'interlayer-cu'
  []
  [tungsten_density]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 19300
      50 19290
      100 19280
      150 19270
      200 19250
      250 19240
      300 19230
      350 19220
      400 19200
      450 19190
      500 19180
      550 19170
      600 19150
      650 19140
      700 19130
      750 19110
      800 19100
      850 19080
      900 19070
      950 19060
      1000 19040
      1100 19010
      1200 18990
    '
    variable = temperature
    property = density
    block = 'armour-w'
  []

  [cucrzr_elastic_modulus]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 128000000000.0
      50 127000000000.0
      100 127000000000.0
      150 125000000000.0
      200 123000000000.0
      250 121000000000.0
      300 118000000000.0
      350 116000000000.0
      400 113000000000.0
      450 110000000000.0
      500 106000000000.0
      550 100000000000.0
      600 95000000000.0
      650 90000000000.0
      700 86000000000.0
    '
    variable = temperature
    property = elastic_modulus
    block = 'pipe-cucrzr'
  []
  [copper_elastic_modulus]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 117000000000.0
      50 116000000000.0
      100 114000000000.0
      150 112000000000.0
      200 110000000000.0
      250 108000000000.0
      300 105000000000.0
      350 102000000000.0
      400 98000000000.0
    '
    variable = temperature
    property = elastic_modulus
    block = 'interlayer-cu'
  []
  [tungsten_elastic_modulus]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 398000000000.0
      50 398000000000.0
      100 397000000000.0
      150 397000000000.0
      200 396000000000.0
      250 396000000000.0
      300 395000000000.0
      350 394000000000.0
      400 393000000000.0
      450 391000000000.0
      500 390000000000.0
      550 388000000000.0
      600 387000000000.0
      650 385000000000.0
      700 383000000000.0
      750 381000000000.0
      800 379000000000.0
      850 376000000000.0
      900 374000000000.0
      950 371000000000.0
      1000 368000000000.0
      1100 362000000000.0
      1200 356000000000.0
    '
    variable = temperature
    property = elastic_modulus
    block = 'armour-w'
  []

  [cucrzr_specific_heat]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 390
      50 393
      100 398
      150 402
      200 407
      250 412
      300 417
      350 422
      400 427
      450 432
      500 437
      550 442
      600 447
      650 452
      700 458
    '
    variable = temperature
    property = specific_heat
    block = 'pipe-cucrzr'
  []
  [copper_specific_heat]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 388
      50 390
      100 394
      150 398
      200 401
      250 406
      300 410
      350 415
      400 419
      450 424
      500 430
      550 435
      600 441
      650 447
      700 453
      750 459
      800 466
      850 472
      900 479
      950 487
      1000 494
    '
    variable = temperature
    property = specific_heat
    block = 'interlayer-cu'
  []
  [tungsten_specific_heat]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      20 129
      50 130
      100 132
      150 133
      200 135
      250 136
      300 138
      350 139
      400 141
      450 142
      500 144
      550 145
      600 147
      650 148
      700 150
      750 151
      800 152
      850 154
      900 155
      950 156
      1000 158
      1100 160
      1200 163
    '
    variable = temperature
    property = specific_heat
    block = 'armour-w'
  []

  [cucrzr_elasticity]
    type = ComputeVariableIsotropicElasticityTensor
    args = temperature
    youngs_modulus = elastic_modulus
    poissons_ratio = 0.33
    block = 'pipe-cucrzr'
  []
  [copper_elasticity]
    type = ComputeVariableIsotropicElasticityTensor
    args = temperature
    youngs_modulus = elastic_modulus
    poissons_ratio = 0.33
    block = 'interlayer-cu'
  []
  [tungsten_elasticity]
    type = ComputeVariableIsotropicElasticityTensor
    args = temperature
    youngs_modulus = elastic_modulus
    poissons_ratio = 0.29
    block = 'armour-w'
  []

  [cucrzr_expansion]
    type = ComputeInstantaneousThermalExpansionFunctionEigenstrain
    temperature = temperature
    stress_free_temperature = ${stressFreeTemp}
    thermal_expansion_function = cucrzr_thermal_expansion
    eigenstrain_name = thermal_expansion_eigenstrain
    block = 'pipe-cucrzr'
  []
  [copper_expansion]
    type = ComputeInstantaneousThermalExpansionFunctionEigenstrain
    temperature = temperature
    stress_free_temperature = ${stressFreeTemp}
    thermal_expansion_function = copper_thermal_expansion
    eigenstrain_name = thermal_expansion_eigenstrain
    block = 'interlayer-cu'
  []
  [tungsten_expansion]
    type = ComputeInstantaneousThermalExpansionFunctionEigenstrain
    temperature = temperature
    stress_free_temperature = ${stressFreeTemp}
    thermal_expansion_function = tungsten_thermal_expansion
    eigenstrain_name = thermal_expansion_eigenstrain
    block = 'armour-w'
  []

  [coolant_heat_transfer_coefficient]
    type = PiecewiseLinearInterpolationMaterial
    xy_data = '
      1 4
      100 ${Arg1}
      150 ${Arg2}
      200 ${Arg3}
      250 ${Arg4}
      295 ${Arg5}
    '
    variable = temperature
    property = heat_transfer_coefficient
    boundary = 'bc-pipe-heattransf'
  []
[]


[BCs]
  [heat_flux_in]
    type = FunctionNeumannBC
    variable = temperature
    boundary = 'bc-top-heatflux'
    function = '${fparse surfHeatFlux}*(1-exp(-10000*t))'
  []
  [heat_flux_out]
    type = ConvectiveHeatFluxBC
    variable = temperature
    boundary = 'bc-pipe-heattransf'
    T_infinity = ${coolantTemp}
    heat_transfer_coefficient = heat_transfer_coefficient
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
  end_time = ${end_time}
  [TimeSteppers]
    [ConstDT1]
      type = ConstantDT
      dt = 0.05
    []

    [ConstDT2]
      type = ConstantDT
      dt = 1
    []
  []
[]

[Controls]
  [c1]
    type = TimePeriod
    enable_objects = 'TimeStepper::ConstDT1'
    disable_objects = 'TimeStepper::ConstDT2'
    start_time = '0'
    end_time = '5'
  []
[]

[Postprocessors]
    [temp_max]
      type = ElementExtremeValue
      variable = temperature
  []
[]

[Outputs]
  exodus = true
[]