pipe_rad_int = 6e-3
pipe_thick = 1.5e-3

interlayer_thick = 2e-3

monoblock_depth = 12e-3
monoblock_side = 3e-3
monoblock_arm_height = 5e-3




pipe_rad_ext = pipe_rad_int+pipe_thick

interlayer_rad_int = pipe_rad_ext
interlayer_rad_ext = interlayer_rad_int+interlayer_thick

monoblock_width = 2*interlayer_rad_ext + 2*monoblock_side
monoblock_height = monoblock_width + monoblock_arm_height

pipe_cent_x = 0.0
pipe_cent_y = interlayer_rad_ext + monoblock_side

print(monoblock_height)
print(monoblock_width)