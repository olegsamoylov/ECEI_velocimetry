"""
to use these functions inside other python programs, paste the following:
import sys
import pathlib
path_of_the_current_file = str(pathlib.Path().absolute())
sys.path.append(path_of_the_current_file+'/modules')
import IDA_Load_osam as IDA
import importlib
importlib.reload(IDA)
then use as
ID=IDA.IDA()
ID.Load(Shot)
ID.Load(Shot, tBegin=0., tEnd=4.)
"""
import sys
sys.path.append("/afs/ipp-garching.mpg.de/aug/ads-diags/common/python/lib")
import numpy as np
import dd_20190506 as dd
# import map_equ_20190429 as equ

class IDAhelp:
    status = False

class IDA:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'IDA', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='IDA', Edition = 0, tBegin=-1.0, tEnd=12.0):
        dd_load = dd.shotfile(Diagnostic, Shotnumber)
        self.Shotnumber = Shotnumber
        self.tBegin = tBegin 
        self.tEnd = tEnd
        print("Reading Te,ne,pe,rhop,time (%g-%g s)"%(tBegin,tEnd))
        self.Te = dd_load( 'Te', tBegin=tBegin, tEnd=tEnd ).data
        self.ne = dd_load('ne', tBegin=tBegin, tEnd=tEnd ).data 
        self.pe = dd_load('pe', tBegin=tBegin, tEnd=tEnd ).data 
        self.rhop = dd_load('rhop', tBegin=tBegin, tEnd=tEnd ).data
        self.time = dd_load( 'time', tBegin=tBegin, tEnd=tEnd )
        print("Loaded")
        dd_load.close()

    def getData_for_t(self, time_point):
        idx_t = self.find_nearest_idx(self.time,time_point)
        self.Te_t = self.Te[idx_t]
        self.ne_t = self.ne[idx_t]
        self.pe_t = self.pe[idx_t]
        self.rhop_t = self.rhop[idx_t]
        self.time_t = self.time[idx_t]
        print("received data for t = %g s" %(self.time_t))

    def find_nearest_idx(self,array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx


