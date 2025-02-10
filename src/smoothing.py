import numpy as np
import scipy as sp
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d

def smooth(x, y, type=None, params=[]):
    if type is None:
        pass
    elif type == 'Savitz-Golay ordem 2':
        y_smooth = savgol_filter(y, window_length=11, polyorder=2)
    elif type == 'Savitz-Golay ordem 3':
        y_smooth = savgol_filter(y, window_length=11, polyorder=3)
    elif type == 'Savitz-Golay ordem 5':
        y_smooth = savgol_filter(y, window_length=11, polyorder=5)
    elif type == 'Savitz-Golay ordem 7':
        y_smooth = savgol_filter(y, window_length=11, polyorder=7)
    elif type == 'Gaussiano sigma=0,5':
        y_smooth = gaussian_filter1d(y, sigma=0.5)
    elif type == 'Gaussiano sigma=2':
        y_smooth = gaussian_filter1d(y, sigma=2)
    elif type == 'Gaussiano sigma=3':
        y_smooth = gaussian_filter1d(y, sigma=3)
    elif type == 'Gaussiano sigma=5':
        y_smooth = gaussian_filter1d(y, sigma=5)
    elif type == 'Média móvel':
        windows = np.lib.stride_tricks.sliding_window_view(y, window_shape=3)
        y_smooth = windows.mean(axis=1)

    return y_smooth