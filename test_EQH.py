import sys
import os
import importlib
import matplotlib.pyplot as plt
import numpy as np
import traceback  # better way to handle exceptions
import pathlib
path_of_the_current_file = str(os.path.dirname(os.path.realpath(__file__)))
os.chdir(path_of_the_current_file)
sys.path.append('/afs/ipp/aug/ads-diags/common/python/lib')
sys.path.append(path_of_the_current_file + '/modules')
import my_funcs_class as my_funcs
import EQH_Load_osam as EQH
importlib.reload(EQH)
importlib.reload(my_funcs)
import map_equ_20190429 as equ

Shot = 25781
time_point = 2.0

EQ = EQH.EQH()
EQ.Load(Shot)
EQ_rhopM = EQ.rhopM
EQ_time = EQ.time
EQ_R = EQ.R
EQ_z = EQ.z
EQ_Rmag = EQ.Rmag
EQ_zmag = EQ.zmag


EQ_rhopM.shape[1]
EQ_Rmag.shape

EQ_R.shape


mf=my_funcs.my_funcs()
mf.cutDataEQH(EQ_time, EQ_rhopM, EQ_R, EQ_z, EQ_Rmag, EQ_zmag, time_point)
mf.rhopM_t
mf.time_t
mf.RR_t
mf.zz_t
mf.Rmag_t
mf.zmag_t

rho_in = 0.3
equ_data = equ.equ_map(Shot, 'EQH', 'AUGD')
data_rz = equ_data.rho2rz(rho_in,time_point,'rho_pol')
R_from_rhop, z_from_rhop = data_rz[0][0][0], data_rz[1][0][0]

# rho2rz(self, rho_in, t_in=None, coord_in='rho_pol', all_lines=False)
contours_rhop = plt.contour(mf.RR_t, mf.zz_t, mf.rhopM_t, 50)
plt.clabel(contours_rhop, inline=True, fontsize=10)
plt.plot(mf.Rmag_t,mf.zmag_t, 'bo')
plt.plot(R_from_rhop, z_from_rhop, 'g-',linewidth=2.0)
plt.show()









print("Script is over.")
