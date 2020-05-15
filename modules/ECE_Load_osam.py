"""
to use these functions inside other python programs, paste the following:
import sys
sys.path.append("/afs/ipp-garching.mpg.de/home/o/osam/workspace/python3_projects/modules_osam")
import ECE_Load_osam as ECE
import importlib
importlib.reload(ECE)
then use as
EC=ECE.ECE()
EC.Load(Shot, Diagnostic='CEC')
"""
import sys
sys.path.append("/afs/ipp-garching.mpg.de/aug/ads-diags/common/python/lib")
import numpy as np
import dd_20190506 as dd
import map_equ_20190429 as equ

class ECEhelp:
    status = False

class ECE:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'CEC', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='CEC', Edition = 0, tBegin=-1.0, tEnd=12.0, eqExp = 'AUGD', eqDiag = 'EQH' ):
        dd_load = dd.shotfile(Diagnostic, Shotnumber)

        self.Shotnumber = Shotnumber
        self.tBegin =tBegin 
        self.tEnd = tEnd

        print("Reading Te")
        self.Te = dd_load( 'Trad-A', tBegin=tBegin, tEnd=tEnd ).data
        print("Reading time")
        self.time =dd_load( 'time-A', tBegin=tBegin, tEnd=tEnd )
        print("Reading R")
        self.R = dd_load('R-A', tBegin=tBegin, tEnd=tEnd ).data 
        print("Reading z")
        self.z = dd_load('z-A', tBegin=tBegin, tEnd=tEnd ).data
        print("Reading rztime")
        self.rztime = dd_load.getTimeBase('rztime', tBegin=tBegin, tEnd=tEnd)
        print("Reading freq")
        self.freq = dd_load.getParameter('parms-A', 'f',dtype=np.float64).data
        self.chs_numbers = np.arange(1,len(self.freq)+1)
        print("Loaded")

        # sorting
        idx_sort = np.argsort(self.freq, axis = 0)[::-1]
        self.Te = self.Te[:,idx_sort]
        self.R = self.R[:,idx_sort]
        self.z = self.z[:,idx_sort]
        self.freq = self.freq[idx_sort]
        self.chs_numbers = self.chs_numbers[idx_sort]
        print("sorted by freqs in descending order")
        dd_load.close()

    """
    def getRhop(self,timepoint=None):
        "get rhop for a timepoint"
        abock = kk.kk()
        abock.Open(self.Shotnumber, diag='EQH')
        idx_t_rz = self.find_nearest_idx(self.rztime, timepoint)
        rhop = abock.Rz_to_rhopol(timepoint, self.R[idx_t_rz,:], self.z[idx_t_rz,:]) 
        return rhop
    """

    def LoadAllRhop(self):
        "load rhop from tBegin until tEnd"
        # abock = kk.kk()
        # abock.Open(self.Shotnumber, diag='EQH')

        equ_data = equ.equ_map(self.Shotnumber, 'EQH', 'AUGD')
        # rhop = np.zeros_like(self.R)
        rhop = equ_data.rz2rho(self.R,self.z,self.rztime,'rho_pol')
            # rhop[j,:] = abock.Rz_to_rhopol(self.rztime[j], self.R[j,:], self.z[j,:]) 
        # for j in xrange(rhop.shape[0]:
        self.rhop = rhop
        print("rhop is loaded")



    """
    def LoadAllRhop_LFS(self):
        dd_load = dd.shotfile('GQH', self.Shotnumber)
        self.Rmag = dd_load.getSignal(b"Rmag")[idxTime]
        self.zmag = dd_load.getSignal(b"Zmag")[idxTime]
        self.Raus = dd_load.getSignal(b"Raus")[idxTime]
        self.zaus = self.zmag
        dd_load.close()


    def LoadAllRhop_LFS(self):
        "load rhop from tBegin until tEnd in LFS"
        abock = kk.kk()
        abock.Open(self.Shotnumber, diag='EQH')
        t_LFS = np.linspace(self.tBegin, self.tEnd, 10)
        R_core_array = np.zeros_like(t_LFS)
        for i in xrange(len(t_LFS)):
            R_core_array[i] = abock.get_special_points(t_LFS[i])['rpfx'][0]
        R_core = np.mean(R_core_array)
        idx_LFS = np.where(np.mean(self.R, axis=0) > R_core)
        rhop = np.zeros_like(self.R)
        for j in xrange(rhop.shape[0]):
            rhop[j,:] = abock.Rz_to_rhopol(self.rztime[j], self.R[j,:], self.z[j,:]) 
        self.rhop = rhop
        self.rhop_LFS = rhop[:,idx_LFS]
        self.Te_LFS = self.Te[:,idx_LFS]
        print("rhop, rhop_LFS, Te_LFS are loaded")
    """


    def remove0chs(self):
        "remove channels that are switched off"
        remove_ch = np.where(np.mean(self.Te, axis=0) == 0.)[0]
        ch = np.arange(self.R.shape[1])
        ch = np.delete(ch, remove_ch)
        self.Te = self.Te[:,ch]
        self.R = self.R[:,ch]
        self.z = self.z[:,ch]
        self.freq = self.freq[ch]
        self.chs_numbers = self.chs_numbers[ch]
        try:
            self.rhop = self.rhop[:,ch]
        except:
            print("!!!Error: Cannot remove0chs from rhop: rhop is not defined")
        print("the following channels are removed:")
        print(remove_ch)

    def find_nearest_idx(self, array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx
