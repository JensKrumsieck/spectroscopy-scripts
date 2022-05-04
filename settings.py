import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
def cm_to_inch(value):
    return value/2.54

def applySettings():
    plt.style.use(['science', 'nature', 'no-latex'])
    plt.rcParams["figure.figsize"] = (cm_to_inch(16), cm_to_inch(13))
    plt.rcParams["figure.dpi"] = 1200
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["axes.titlesize"] = 9
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams["font.family"] = "Arial"

def colorMap(num_spc):
    colors = [(0, 0, 0), (1, 0, 0)] # first color is black, last is red
    cm = LinearSegmentedColormap.from_list(
            "Custom", colors, N=20)
    cols = cm(np.linspace(0,1,int(num_spc/2) ))
    return cols