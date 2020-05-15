"""
to use these functions inside other python programs, paste the following:
import sys
sys.path.append("/afs/ipp-garching.mpg.de/home/o/osam/workspace/python3_projects/modules_osam")
import EQH_Load_osam as EQH
import importlib
importlib.reload(EQH)
then use as
EQ=EQH.EQH()
EQ.Load(Shot)
EQ.Load(Shot, tBegin = 2.0, tEnd = 4.0)
"""
import sys
sys.path.append("/afs/ipp-garching.mpg.de/aug/ads-diags/common/python/lib")
import numpy as np
import dd_20190506 as dd
from scipy.interpolate import interp1d
# import map_equ_20190429 as equ

class EQHhelp:
    status = False

class EQH:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'EQH', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='EQH', Edition = 0, tBegin=-1.0, tEnd=12.0):
        dd_load = dd.shotfile(Diagnostic, Shotnumber)

        self.Shotnumber = Shotnumber
        self.tBegin =tBegin 
        self.tEnd = tEnd

        self.Nz = dd_load.getParameter(b'PARMV',b'N').data+1
        self.NR = dd_load.getParameter(b'PARMV',b'M').data+1
        Ntime = dd_load.getParameter(b'PARMV',b'NTIME').data
        time = (dd_load.getSignal(b"time"))[0:Ntime]
        idxTime = np.where( (time>=tBegin) & (time<=tEnd) )[0]
        self.time = time[idxTime]

        self.R = (dd_load.getSignalGroup(b"Ri"))[0:Ntime,0:self.NR][idxTime]
        self.z = (dd_load.getSignalGroup(b"Zj"))[0:Ntime,0:self.Nz][idxTime]
        self.PsiOrigin = dd_load.getObjectData(b"PFM")[0:Ntime,0:self.Nz,0:self.NR][idxTime]
        ###magnetic axis,sxm
        self.PsiSpecial = dd_load.getObjectData(b"PFxx")[0:Ntime][idxTime]   
        ##time, R, z
        self.Psi = np.swapaxes(self.PsiOrigin,1,2)
        self.PsiAxis = self.PsiSpecial[:,0]
        self.PsiSep = self.PsiSpecial[:,1]

        self.rhopM = np.sqrt(np.abs((self.Psi.T-self.PsiAxis)/(self.PsiSep-self.PsiAxis))).T
        self.rhopM = np.swapaxes(self.rhopM,1,2)



        dd_load.close()
        # try:
        dd_load = dd.shotfile('GQH', self.Shotnumber)
        self.Rmag = dd_load.getSignal(b"Rmag")[idxTime]
        self.zmag = dd_load.getSignal(b"Zmag")[idxTime]
        self.Raus = dd_load.getSignal(b"Raus")[idxTime]
        self.zaus = self.zmag
        dd_load.close()
        # except:
            # print("Special points are not loaded (couldn't load GQH")


    def getrRhop_forTime(self, time_point):
        """
        linear interpolation of rhopM for
        a given time point
        """
        rhopM_t = np.zeros([self.Nz,self.NR])
        idx_B = np.searchsorted(self.time, time_point, side='right') -1
        idx_E = np.searchsorted(self.time, time_point, side='right')
        for i_Nz in range(self.Nz):
            linfit = interp1d([self.time[idx_B],self.time[idx_E]], np.vstack([self.rhopM[idx_B,i_Nz,:], self.rhopM[idx_E,i_Nz,:]]), axis=0)
            rhopM_t[i_Nz,:] = linfit(time_point)
        self.rhopM_t = rhopM_t
        # R and z are constant in time (no interp needed)
        self.R_t = self.R[idx_B]
        self.z_t = self.z[idx_B]
        RR_t, zz_t = np.meshgrid(self.R_t,self.z_t)
        self.RR_t = RR_t
        self.zz_t = zz_t
        self.t_point = time_point
        print("rhopM lin interp for t=%g s, between tB=%g s,tE=%g s" %(time_point,self.time[idx_B],self.time[idx_E]))

