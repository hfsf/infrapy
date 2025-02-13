#Classe que armazena um espectrograma
import numpy as np
import pandas as pd

class SpectrumSet:

    def init(self, *spectrums):
        self.spectrums = list(spectrums)


class Spectrum:

    def __init__(self):

        self.data = None
        self.normalized_data = None
        self.smooth_data = None

        self.axis_names = ['cm-1', '%T']
        self.name = None

    def __getitem__(self, *idxs):
        pass
    
    def __add__(self, another_spectrum):
        if isinstance(another_spectrum, Spectrum):
            if self.data.iloc[:,0].size == another_spectrum.iloc[:, 0].size:
                rtrn = Spectrum()
                rtrn.axis_names = self.axis_names
                rtrn.name = self.name+"+"+another_spectrum.name
                rtrn.data.iloc[:,1] = self.data.iloc[:,1] + another_spectrum.data.iloc[:,1]
                return rtrn
            else:
                raise Exception("Error: Unequal size of spectrums")

    def __sub__(self, another_spectrum):
        if isinstance(another_spectrum, Spectrum):
            if self.data.iloc[:,0].size == another_spectrum.iloc[:, 0].size:
                rtrn = Spectrum()
                rtrn.axis_names = self.axis_names
                rtrn.name = self.name+"-"+another_spectrum.name
                rtrn.data.iloc[:,1] = self.data.iloc[:,1] - another_spectrum.data.iloc[:,1]
                return rtrn
            else:
                raise Exception("Error: Unequal size of spectrums")

    def normalize(self):
        x = self.data.iloc[:, 0].to_numpy()
        y = self.data.iloc[:, 1].to_numpy()

        if np.any(y > 100.):
            y_norm = 100. * (y / np.max(y))

        self.normalized_data = np.array([x, y_norm])    
    
    def load(self, file_name):
        self.data = pd.read_csv(file_name, sep='\t', skiprows=3, decimal=',', comment='#')
        self.data.columns = self.axis_names

    @property
    def x(self):
        if self.normalized_data is not None:
            return self.data.iloc[:,0].to_numpy()
        else:
            return self.normalized_data.iloc[:, 0].to_numpy()
    
    @property
    def y(self):
        if self.normalized_data is not None:
            return self.data.iloc[:,1].to_numpy()
        else:
            return self.normalized_data.iloc[:, 1].to_numpy()