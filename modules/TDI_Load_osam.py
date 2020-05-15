"""
to use these functions inside other python programs, paste the following:
import sys
import pathlib
path_of_the_current_file = str(pathlib.Path().absolute())
sys.path.append(path_of_the_current_file+'/modules')
import TDI_Load_osam as TDI
import importlib
importlib.reload(TDI)
then use as
TD=TDI.TDI()
TD.Load(Shot)
TD.Load(Shot, tBegin = 2.0, tEnd = 4.0)
"""
import sys
sys.path.append("/afs/ipp-garching.mpg.de/aug/ads-diags/common/python/lib")
import numpy as np
import dd_20190506 as dd
import map_equ_20190429 as equ

class TDIhelp:
    status = False

class TDI:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'TDI', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='TDI', Edition = 0):
        dd_load = dd.shotfile(Diagnostic, Shotnumber, 'AUGD')

        self.Shotnumber = Shotnumber
        # self.tBegin = tBegin 
        # self.tEnd = tEnd
        tOffsB = -0.02
        tOffsE = 0.01

        time = dd_load.getTimeBase(b't1')
        print("tBegin = %g s ; tEnd = %g s" %(time[0],time[-1]))
        N_LOS, N_R = 20, 8
        Sig1 = dd_load.getObjectData(b'Sig1')
        print("Sig group 1/4 loaded")
        Sig2 = dd_load.getObjectData(b'Sig2')
        print("Sig group 2/4 loaded")
        Sig3 = dd_load.getObjectData(b'Sig3')
        print("Sig group 3/4 loaded")
        Sig4 = dd_load.getObjectData(b'Sig4')
        print("Sig group 4/4 loaded")
        print("TDI data has been loaded")
        iOffsB = self.find_nearest_idx(time, tOffsB)
        iOffsE = self.find_nearest_idx(time, tOffsE)
        Sigs_together = np.concatenate((Sig1,Sig2,Sig3,Sig4),axis=0)
        # Sigs_together_offs = np.concatenate((Sig1_offs,Sig2_offs,Sig3_offs,Sig4_offs),axis=0)
        Sigs_together_offs = Sigs_together.copy()[:, iOffsB:iOffsE]

        S_offset=np.zeros(192)
        for i in range(192):
            S_offset[i]= 8191 - np.abs(np.mean(Sigs_together_offs[i,:]))
        ECEId = np.zeros([N_LOS,N_R,Sigs_together.shape[1]])
        idx_per_LOS = 0
        for L_i in range(N_LOS):
            for R_i in range(N_R):
                ECEId[L_i,7-R_i] = Sigs_together[idx_per_LOS+R_i,:] + S_offset[idx_per_LOS+R_i] - 8191  # put R chs in reverse order and remove offset
            idx_per_LOS += N_R
        print("ECEId matrix has been created")
        ECEId = np.swapaxes(ECEId.T,1,2)
        self.ECEId = ECEId
        self.time = time
        dd_load.close()


    def Load_FakeRz(self):
        """
        Calculate fake ECEI window position
        (Ray tracing should be a proper way)
        """
        from scipy.constants import e, m_e 
        N_LOS, N_R = 20, 8
        path_to_eceilog = '/afs/ipp-garching.mpg.de/home/e/ecei/LOG_ECEI/'
        with open(path_to_eceilog+"%d.log"%(self.Shotnumber), 'r') as f:
            ECEI_LOG = f.read()
        Bt = float(ECEI_LOG.split(" ")[1])
        f_LO = float(ECEI_LOG.split(" ")[3])
        self.Bt = Bt
        self.f_LO = f_LO 
        f_0 = 2.8 # [GHz]
        # f_0 = 3.7 # [GHz]
        ch_spacing = 800 # MHz
        R0 = 1.65 # [m] AUG main radius
        f_array  = np.zeros(N_R)
        z_array  = np.zeros(N_LOS)
        dz = 0.0322 # [m] - fake dz between LOSs
        z_up = 0.3165 # [m] - fake LOS1 z position
        # z_up = 0.5165 # [m] - fake LOS1 z position


        f_array[0] = f_LO + f_0  # [GHz]
        for i in range(N_R-1):
            f_array[i+1] = f_array[0]+ch_spacing*1e-3*(1+i) # [GHz]

        z_array[0] = z_up
        for i in range(N_LOS-1):
            z_array[i+1] = z_array[0] - dz*(i+1)

        R_array = 2*e*np.abs(Bt)*R0/(2*np.pi*m_e*f_array*1.e9)
        R_array = R_array[::-1]
        RR_array, zz_array = np.meshgrid(R_array,z_array)



        self.R_fake = R_array
        self.z_fake = z_array
        self.RR_fake = RR_array
        self.zz_fake = zz_array
        self.N_LOS = N_LOS
        self.N_R = N_R
        # slef.ECEIrhopM = ECEIrhopM
        print("FakeRz has been loaded")
        

    def find_nearest_idx(self,array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx
