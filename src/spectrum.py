#Classe que armazena um espectrograma
import numpy as np
import pandas as pd
import smoothing

class SpectrumSet:

    def __init__(self, *spectrums):
        self.spectrums = []
        for spc in spectrums:
            if isinstance(spc, Spectrum):
                self.spectrums.append(spc)
            elif isinstance(spc, SpectrumSet):
                self.spectrums = self.spectrums + spc.spectrums     
    
    def __getitem__(self, index):
        """
        Overloaded function for indexing spectrums inside SpectrumSet
        """
        try:
            return self.spectrums[index]
        except:
            raise ValueError("Index not present in SpectrumSet")

    def normalize(self):
        """
        Normalize all Spectrum contained in the SpectrumSet
        """
        for spc in self.spectrums:
            spc.normalize()

    def smooth(self, type='Gaussiano sigma=2'):
        """
        Smooth all spectrum contained in the SpectrumSet
        """
        for spc in self.spectrums:
            spc.smooth(type)

class Spectrum:

    def __init__(self):

        self.data = None
        self.normalized_data = None
        self.smooth_data = None

        self.axis_names = ['cm-1', '%T']
        self.name = None

    def __rshift__(self, another_spectrum):
        """
        Overloaded method for joining two Spectrum into a SpectrumSet
        """
        return SpectrumSet(self, another_spectrum)

    def __getitem__(self, keys):
        """
        Numpy style indexing for Spectrum variables. Useful for croping spectrograms
        """

        x_col = self.data.colummns[0]
        y_col = self.data.colummns[0]

        x_slice, y_slice = self._parse_keys(keys)

        filtered_data = self.data.copy()

        if x_slice is not None:
            x_start = x_slice.start if x_slice.start is not None else -np.inf
            x_end = x_slice.stop if x_slice.stop is not None else np.inf
            filtered_data = filtered_data[(filtered_data[x_col] >= x_start) & 
                                         (filtered_data[x_col] <= x_end)
                                         ]
        if y_slice is not None:
            y_start = y_slice.start if y_slice.start is not None else -np.inf
            y_end = y_slice.stop if y_slice.stop is not None else np.inf
            filtered_data = filtered_data[(filtered_data[y_col] >= y_start) & 
                                         (filtered_data[y_col] <= y_end)
                                         ]
        return filtered_data

    def _parse_keys(self, key):
        """
        Parsing slices used for spectrogram slicing
        """
        #1d slice -> only for first dimension (eg: A[10:1500])
        if isinstance(key, slice):
            return(key, slice(None, None))
        #2d slice -> two dimensions -> check for incomplete keys (eg: A[:, 10:1500])
        elif isinstance(key, tuple):
            if len(key) > 2:
                raise ValueError("Spectrogram has only 2 dimensions (x, y)")
            else:
                x_slice = key[0] if len(key) >= 1 else slice(None, None)
                y_slice = key[1] if len(key) >= 2 else slice(None, None)

                return (x_slice, y_slice)
        else:
            raise ValueError("Invalid index for spectrogram")

    def __add__(self, another_spectrum):
        if isinstance(another_spectrum, Spectrum):
            if self.data.iloc[:,0].size == another_spectrum.data.iloc[:, 0].size:
                rtrn = Spectrum()
                rtrn.axis_names = self.axis_names
                rtrn.name = self.name+"+"+another_spectrum.name
                rtrn.data.iloc[:,1] = self.data.iloc[:,1] + another_spectrum.data.iloc[:,1]
                return rtrn
            else:
                raise Exception("Error: Unequal size of spectrums")

    def __sub__(self, another_spectrum):
        if isinstance(another_spectrum, Spectrum):
            if self.data.iloc[:,0].size == another_spectrum.data.iloc[:, 0].size:
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

        self.normalized_data = np.array([x, y_norm]).T    
    
    def load(self, file_name):
        self.data = pd.read_csv(file_name, sep='\t', skiprows=3, decimal=',', comment='#')
        self.data.columns = self.axis_names

    def smooth(self, type='Gaussiano sigma=2'):
        self.data.iloc[:, 1] = smoothing.smooth(self.x, self.y, type)

    @property
    def x(self):
        if self.normalized_data is not None:
            return self.normalized_data[:,0]
        else:
            return self.data.iloc[:, 0].to_numpy()
    
    @property
    def y(self):
        if self.normalized_data is not None:
            return self.normalized_data[:,1]
        else:
            return self.data.iloc[:, 1].to_numpy()