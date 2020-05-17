"""
to use these functions inside other python programs, paste the following:
import sys
import pathlib
path_of_the_current_file = str(pathlib.Path().absolute())
sys.path.append(path_of_the_current_file+'/modules')
import my_funcs_class as my_funcs
importlib.reload(my_funcs)
then use as
mf=my_funcs.my_funcs()
mf.find_nearest_idx(array, value)
"""
import sys
# sys.path.append("/afs/ipp-garching.mpg.de/aug/ads-diags/common/python/lib")
import numpy as np
import pathlib
path_of_the_current_file = str(pathlib.Path().absolute())
sys.path.append(path_of_the_current_file+'/modules')
sys.path.append(path_of_the_current_file)


class my_funcs:
    def __init__( self ):
        pass

    def find_nearest_idx(self,array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx


    def Fourier_analysis_ECEI_lowpass(self, time, ECEId, noise_level, f_cut):
        ECEId_fft = np.zeros_like(ECEId,dtype=complex)
        ECEId_fft_f = np.zeros_like(ECEId,dtype=complex)
        ECEId_fft_f_ifft = np.zeros_like(ECEId)
        ECEId_fft_freq = np.zeros_like(ECEId)
        N_LOS, N_R = ECEId.shape[1], ECEId.shape[2]
        ECEId_fft_noise = np.zeros([N_LOS, N_R])
        for LL in range(N_LOS):
            for RR in range(N_R):
                ECEId_fft_freq[:,LL,RR], ECEId_fft[:,LL,RR], offset = self.fft_analysis(time, ECEId[:,LL,RR])
                noise_level_value = np.max(np.abs(ECEId_fft[:,LL,RR]))*noise_level
                ECEId_fft_noise[LL,RR] = noise_level_value
                ECEId_fft_f[:,LL,RR] = self.set_to_0_below_level_within_range_lowpass(ECEId_fft_freq[:,LL,RR], ECEId_fft[:,LL,RR], noise_level_value, f_cut)
                ECEId_fft_f_ifft[:,LL,RR] = self.inverse_fft(ECEId_fft_f[:,LL,RR],offset)
        
        self.ECEId_fft = ECEId_fft
        self.ECEId_fft_freq = ECEId_fft_freq
        self.ECEId_fft_f = ECEId_fft_f
        self.ECEId_fft_f_ifft = ECEId_fft_f_ifft
        self.ECEId_fft_noise = ECEId_fft_noise
        print("Fourier lowpass filter:")
        print("f_cut_lowpass = %g kHz, ampl_cut_lowpass = %g" %(f_cut*1e-3, noise_level))
        print("self.ECEId_fft, self.ECEId_fft_freq, self.ECEId_fft_f, self.ECEId_fft_f_ifft, ECEId_fft_noise are loaded.\n")


    def Fourier_analysis_ECEI_highpass(self, time, ECEId, noise_level, f_cut):
        ECEId_fft = np.zeros_like(ECEId,dtype=complex)
        ECEId_fft_f = np.zeros_like(ECEId,dtype=complex)
        ECEId_fft_f_ifft = np.zeros_like(ECEId)
        ECEId_fft_freq = np.zeros_like(ECEId)
        N_LOS, N_R = ECEId.shape[1], ECEId.shape[2]
        ECEId_fft_noise = np.zeros([N_LOS, N_R])
        for LL in range(N_LOS):
            for RR in range(N_R):
                ECEId_fft_freq[:,LL,RR], ECEId_fft[:,LL,RR], offset = self.fft_analysis(time, ECEId[:,LL,RR])
                noise_level_value = np.max(np.abs(ECEId_fft[:,LL,RR]))*noise_level
                ECEId_fft_noise[LL,RR] = noise_level_value
                ECEId_fft_f[:,LL,RR] = self.set_to_0_below_level_within_range_highpass(ECEId_fft_freq[:,LL,RR], ECEId_fft[:,LL,RR], noise_level_value, f_cut)
                ECEId_fft_f_ifft[:,LL,RR] = self.inverse_fft(ECEId_fft_f[:,LL,RR],offset)
        
        self.ECEId_fft = ECEId_fft
        self.ECEId_fft_freq = ECEId_fft_freq
        self.ECEId_fft_f = ECEId_fft_f
        self.ECEId_fft_f_ifft = ECEId_fft_f_ifft
        self.ECEId_fft_noise = ECEId_fft_noise
        print("Fourier highpass filter:")
        print("f_cut_highpass = %g kHz, ampl_cut_highpass = %g" %(f_cut*1e-3, noise_level))
        print("self.ECEId_fft, self.ECEId_fft_freq, self.ECEId_fft_f, self.ECEId_fft_f_ifft, ECEId_fft_noise are loaded.\n")




    def fft_analysis(self, t, y):
        " returns freq and normalized(fft(y)) and offset "
        " apply Y[range(s_length/2)] "
        Ts = t[1] - t[0] # sampling interval
        Fs = 1.0/Ts # sampling rate
        s_length = len(t) # length of the signal
        k = np.arange(s_length) # coef for calc freq
        T = s_length/Fs # coef for calc freq
        frq = k/T # two sides frequency range
        # frq =frq[range(s_length/2)] # one side frequency range 
        offset = np.mean(y)
        y_ed = y - offset
        Y = np.fft.fft(y_ed)/s_length # fft computing and normalization
        # Y = Y[range(s_length/2)]
        return frq, Y, offset


    def set_to_0_below_level_within_range_lowpass(self,freq, Y, level, f_cut):
        "returns array with elements set to 0 below certain level within a certain range"
        NN_len = len(freq)
        idx_freq = self.find_nearest_idx(freq[:int(NN_len/2)], f_cut) 
        Y2 = Y.copy()
        idx_cut = (np.abs(Y2[idx_freq:NN_len-idx_freq]) <= level) 
        Y2[idx_freq:NN_len-idx_freq][idx_cut] = 0.0
        return Y2


    def set_to_0_below_level_within_range_highpass(self,freq, Y, level, f_cut):
        "returns array with elements set to 0 below certain level within a certain range"
        NN_len = len(freq)
        idx_freq = self.find_nearest_idx(freq[:int(NN_len/2)], f_cut) 
        Y2 = Y.copy()
        idx_cut1 = (np.abs(Y2[:idx_freq]) <= level) 
        idx_cut2 = (np.abs(Y2[NN_len-idx_freq:]) <= level) 
        Y2[:idx_freq][idx_cut1] = 0.0
        Y2[NN_len-idx_freq:][idx_cut2] = 0.0
        return Y2


    def inverse_fft(self, Y, offset):
        "returns inverse fft from Y"
        return np.real(len(Y)*np.fft.ifft(Y)) + offset
    
    
    
    def Fourier_analysis_ECEI_multiple(self, time, ECEId, f_hp, f_lp):
        " Fourier filter for multiple frequencies"
        freq_num = len(f_hp)
        NN_len = len(time)
        ECEId_fft = np.zeros_like(ECEId,dtype=complex)
        ECEId_fft_f = np.zeros_like(ECEId,dtype=complex)
        ECEId_fft_f_ifft = np.zeros_like(ECEId)
        ECEId_fft_freq = np.zeros_like(ECEId)
        N_LOS, N_R = ECEId.shape[1], ECEId.shape[2]
        for LL in range(N_LOS):
            for RR in range(N_R):
                ECEId_fft_freq[:,LL,RR], ECEId_fft[:,LL,RR], offset = self.fft_analysis(time, ECEId[:,LL,RR])
                ECEId_fft_new = np.zeros_like(ECEId_fft[:,LL,RR])
                for i in range(freq_num):
                    idxB = self.find_nearest_idx(ECEId_fft_freq[:,LL,RR][:int(NN_len/2)], f_hp[i])
                    idxE = self.find_nearest_idx(ECEId_fft_freq[:,LL,RR][:int(NN_len/2)], f_lp[i])
                    if (idxB == idxE):
                        idxE += 1
                    ECEId_fft_new[idxB:idxE] = ECEId_fft[:,LL,RR][idxB:idxE].copy()
                    ECEId_fft_new[NN_len-idxE:NN_len-idxB] = ECEId_fft[:,LL,RR][NN_len-idxE:NN_len-idxB]
                ECEId_fft_f[:,LL,RR] =  ECEId_fft_new.copy()
                ECEId_fft_f_ifft[:,LL,RR] = self.inverse_fft(ECEId_fft_new,offset)
                
        self.ECEId_fft = ECEId_fft
        self.ECEId_fft_freq = ECEId_fft_freq
        self.ECEId_fft_f = ECEId_fft_f
        self.ECEId_fft_f_ifft = ECEId_fft_f_ifft
        print("Fourier multiple filter applied.")
        print("self.ECEId_fft, self.ECEId_fft_freq, self.ECEId_fft_f, self.ECEId_fft_f_ifft are loaded.\n")
    
    


    def SavGol_filter_ECEI(self, ECEI_data, win_len, pol_ord):
        from scipy.signal import savgol_filter
        print("Applying SavGol filter with win_len = %g, pol_ord = %g" %(win_len, pol_ord))
        N_LOS = ECEI_data.shape[1]
        N_R = ECEI_data.shape[2]
        #
        ECEId_savgol = np.zeros_like(ECEI_data)
        #
        try:
            for NL in range(N_LOS):
                for NR in range(N_R):
                    ECEI_data[np.isnan(ECEI_data)] = 0.0
                    ECEId_savgol[:, NL, NR] = savgol_filter(ECEI_data[:, NL, NR], win_len, pol_ord)
            #
            self.ECEId_savgol = ECEId_savgol
            #
            print("SavGol filter is applied")
            print("The attribute is written as 'self.ECEId_savgol'.\n")

        except Exception as exc:
            print("!!! SavGol filter NOT applied. ERROR: %s"%(exc))
            self.ECEId_savgol = ECEId_savgol # save zeros


    def CutDataECEI(self, time, ECEId, tBegin = -1., tEnd = -12.):
        """
        Cut the data for the time interval
        from tBegin to tEnd
        """
        idxB = self.find_nearest_idx(time,tBegin)
        idxE = self.find_nearest_idx(time,tEnd )
        # self.tBegin = self.time[idxB]
        # self.tEnd = self.time[idxE]
        self.time_C = time[idxB:idxE]
        self.ECEId_C = ECEId[idxB:idxE,:,:]
        print("ECEId data is sliced: tB = %g, tE = %g"%(self.time_C[0],self.time_C[-1]))
        print("The attribute is written as 'self.ECEId_C','self.time_C'.\n")

    def cutDataEQH(self, time, rhopM, R, z,
            Rmag, zmag, time_point):
        """
        Cut the data for the given time point
        linear interpolate rhopM, Rmag, zmag
        R and z are not required to be intrepolated
        because they are constant matrices
        """
        from scipy.interpolate import interp1d
        Nz, NR = rhopM.shape[1], rhopM.shape[2]
        rhopM_t = np.zeros([Nz,NR])
        idx_B = np.searchsorted(time, time_point, side='right') -1
        idx_E = np.searchsorted(time, time_point, side='right')
        for i_Nz in range(Nz):
            linfit = interp1d([time[idx_B],time[idx_E]], np.vstack([rhopM[idx_B,i_Nz,:], rhopM[idx_E,i_Nz,:]]), axis=0)
            rhopM_t[i_Nz,:] = linfit(time_point)
            
        # linear interp Rmag and zmag
        linfit = interp1d([time[idx_B],time[idx_E]], np.vstack([Rmag[idx_B], Rmag[idx_E]]), axis=0)
        self.Rmag_t = linfit(time_point)
        linfit = interp1d([time[idx_B],time[idx_E]], np.vstack([zmag[idx_B], zmag[idx_E]]), axis=0)
        self.zmag_t = linfit(time_point)
        # R and z matrices are constant in time (no interp needed)
        self.rhopM_t = rhopM_t
        self.R_t = R[idx_B]
        self.z_t = z[idx_B]
        self.RR_t, self.zz_t = np.meshgrid(self.R_t,self.z_t)
        self.time_t = time_point
        print("rhopM lin interp for t=%g s, between tB=%g s,tE=%g s"
                %(time_point, time[idx_B], time[idx_E]))
        

    def relECEI(self, ECEI_data):
        """
        relative delta T / <T>
        """
        ECEId_rel = np.zeros_like(ECEI_data)
        N_LOS = ECEI_data.shape[1]
        N_R = ECEI_data.shape[2]
        #
        for NL in range(N_LOS):
            for NR in range(N_R):
                    ECEId_rel[:, NL, NR] = (ECEI_data[:, NL, NR] - np.mean(ECEI_data[:, NL, NR]) )/ \
                                        np.mean(ECEI_data[:, NL, NR])
        #
        self.ECEId_rel = ECEId_rel
        print("ECEI deltaTrad/<Trad> is calculated.")
        print("The attribute is written as 'self.ECEId_rel'.\n")


    def Cross_cal_IDA(self, Shotnumber, ECEI_data, ECEI_time, RR, zz, tCalB, tCalE):
        try:
            print("+++ Loading IDA... +++")
            import sys
            import IDA_Load_osam as IDA
            sys.path.append("/afs/ipp-garching.mpg.de/aug/ads-diags/common/python/lib")
            import map_equ_20190429 as equ
            from scipy import interpolate
            ID=IDA.IDA()
            ID.Load(Shotnumber, tBegin=tCalB, tEnd=tCalE)
            print("+++ IDA: tB = %g, tE = %g  +++"%(ID.time[0], ID.time[-1]))
            print("+++ IDA Loaded +++")

            idx_t_ECEIcalB = self.find_nearest_idx(ECEI_time, tCalB)
            idx_t_ECEIcalE = self.find_nearest_idx(ECEI_time, tCalE)

            N_LOS, N_R = ECEI_data.shape[1],ECEI_data.shape[2]
            # get rhopM for FakeRz
            # only for one time point so far (change in the future)
            equ_data = equ.equ_map(Shotnumber, 'EQH', 'AUGD')
            ECEIrhopM = np.zeros([N_LOS,N_R])
            time_rhopM = tCalB + (tCalE - tCalB)/2.0

            for i_z in range(N_LOS):
                ECEIrhopM[i_z,:] = equ_data.rz2rho(RR[i_z,:],zz[i_z,:],time_rhopM,'rho_pol')
            print("+++ ECEIrhopM has been created t = %g s +++"%(time_rhopM))

            Te_mean_IDA = np.mean(ID.Te[:, :], axis=0)
            rhop_mean_IDA = np.mean(ID.rhop[:, :], axis=0)
            f_IDA = interpolate.interp1d(rhop_mean_IDA, Te_mean_IDA)

            # mean of ECEI data from tBegin to tEnd
            Te_mean_ECEI = np.zeros((N_LOS,N_R))
            rhop_mean_ECEI = np.zeros((N_LOS,N_R))


            for i in range(N_LOS):
                Te_mean_ECEI[i,:] = np.mean(ECEI_data[idx_t_ECEIcalB:idx_t_ECEIcalE, i, :] , axis = 0)
            rhop_mean_ECEI = ECEIrhopM.copy() # !!! should be replaced with mean over the cal time

            # Calibration
            ECEId_cal = np.zeros_like(ECEI_data)
            for i in range(N_LOS):
                for j in range(N_R):
                        ECEId_cal[:, i, j] = ECEI_data[:, i, j] * f_IDA(rhop_mean_ECEI[i, j]) / Te_mean_ECEI[i, j]

            self.ECEId_cal = ECEId_cal
            print("+++ ECEI cross cal with IDA successfully +++")

        except Exception as exc:
            print("!!! Couldn't cross calibrate. ERROR: %s"%(exc))


    def dataBinning(self, time, data, samplefreq = 1.0 ):                        
        # print("binning with %g kHz" %samplefreq)
        ntimes= np.size(time)
        samplingrate = 1.0/np.mean(np.diff(time))
        dataShape =np.array(np.shape(data))  
        #get the time index
        idxOfTime = np.squeeze(np.where(dataShape == ntimes))
        # if more index with the number of times exists, take the first one
        if np.size(idxOfTime) > 1:
            idxOfTime = idxOfTime[0]

        bins = int(ntimes*(float(samplefreq)*1.0e3/samplingrate))

        slices= np.linspace(0, ntimes, bins+1, True).astype(int)
        counts = np.diff(slices)

        #calculate new timebase
        newTime = np.add.reduceat(time, slices[:-1]) / counts
        newNtimes = np.size(newTime)

        #create new shape
        newDataShape = dataShape
        #replace old shape
        np.put(newDataShape, idxOfTime, newNtimes)
        #create new Data array
        newData = np.zeros( (newDataShape) )

        #simplify array such as the first index is always the timebase
        newData = np.swapaxes(newData,0,idxOfTime)
        data = np.swapaxes( data,0,idxOfTime )

        storeShape = np.shape( newData )

        # rehape data to two dimensions
        data = np.reshape(data,(ntimes,int(np.size(data)/ntimes)))
        newData = np.reshape(newData,(newNtimes,int(np.size(newData)/newNtimes)))

        for i in range(np.shape(data)[1]):
            newData[:,i] = np.add.reduceat(data[:,i], slices[:-1]) / counts

        #shape back
        newData = np.reshape(newData,(storeShape))
        #swap back to original shape
        newData = np.swapaxes(newData,0,idxOfTime)

        return newTime,newData


    def dataBinningECEI(self, time, data, samplefreq = 1.0 ):                        
        print("binning with %g kHz" %samplefreq)

        NN_LOS, NN_R = data.shape[1], data.shape[2]

        # find length of new time database
        ntimes= np.size(time)
        samplingrate = 1.0/np.mean(np.diff(time))
        bins = int(ntimes*(float(samplefreq)*1.0e3/samplingrate))
        slices= np.linspace(0, ntimes, bins+1, True).astype(int)
        counts = np.diff(slices)
        #calculate new timebase
        newTime = np.add.reduceat(time, slices[:-1]) / counts
        newNtimes = np.size(newTime)
        new_data_base = np.zeros([newNtimes,NN_LOS,NN_R])

        for L_i in range(NN_LOS):
            for R_i in range(NN_R):
                    newTime,new_data_base
                    data_1D = data[:,L_i,R_i].copy()
                    new_time_base, new_data_base[:,L_i,R_i] = self.dataBinning(time, data_1D,samplefreq)
                    
        return new_time_base,new_data_base

    def bilateral_filter(self,data,kernel,kern_size,s0,s1):
        from skimage.morphology import disk,square
        from skimage.filters import rank
        import numpy as np
        # https://scikit-image.org/docs/dev/api/skimage.filters.rank.html?highlight=mean_bilateral
        if (kernel == "disk"):
            selem = disk(kern_size)
        if (kernel == "square"):
            selem = square(kern_size)
        data_norm = 1.0*data/np.max(np.abs(data)) 
        data_filt = rank.mean_bilateral(data_norm, selem=selem, s0=s0, s1=s1)
        return data_filt

    def median_filter(self,data,kernel,kern_size):
        from scipy import ndimage
        from skimage.morphology import disk, square
        if (kernel == "disk"):
            footprint = disk(kern_size)
        if (kernel == "square"):
            footprint = square(kern_size)
        data_filt =  ndimage.median_filter(data,footprint = footprint, mode = 'nearest')
        return data_filt
    
    def conservative_smoothing_filter(self, data, filter_size):
        # https://towardsdatascience.com/image-filters-in-python-26ee938e57d2
        temp = []
    
        indexer = filter_size // 2
        
        new_image = data.copy()
        
        nrow, ncol = data.shape
        
        for i in range(nrow):
            
            for j in range(ncol):
                
                for k in range(i-indexer, i+indexer+1):
                    
                    for m in range(j-indexer, j+indexer+1):
                        
                        if (k > -1) and (k < nrow):
                            
                            if (m > -1) and (m < ncol):
                                
                                temp.append(data[k,m])
                                
                temp.remove(data[i,j])
                
                
                max_value = max(temp)
                
                min_value = min(temp)
                
                if data[i,j] > max_value:
                    
                    new_image[i,j] = max_value
                
                elif data[i,j] < min_value:
                    
                    new_image[i,j] = min_value
                
                temp =[]
        
        return new_image.copy()
        
    def gaussian_filter(self,data,sigma):
        from scipy.ndimage import gaussian_filter
        data_filt = gaussian_filter(data,sigma,mode="nearest")
        return data_filt

    def nan_interp_2d(self,A):
        from scipy import interpolate
        n,m = A.shape
        x,y = np.mgrid[0:n,0:m]
        mask = ~np.isnan(A) # ~ bitwise complement operator (the same but minus one)
        interp = interpolate.interp2d(x[mask], y[mask], A[mask],kind="cubic")
        xn,yn = np.arange(n), np.arange(m)
        result = interp(xn,yn).T
        return result
