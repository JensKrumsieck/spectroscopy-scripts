import argparse
from locale import normalize
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import (
    AutoLocator, AutoMinorLocator)
from settings import applySettings


applySettings()

### ARGPARSE ###
parser = argparse.ArgumentParser(prog='UV/Vis Plotter')
parser.add_argument("files", help="specify multi structural cif file", nargs='+')
parser.add_argument("-n", "--nonorm", action='store_true',  help="do not normalize")
parser.add_argument("-l", "--labels", nargs='+',  help="labels")
args = parser.parse_args()

### END ARGPARSE ###

def getMax(y: pd.Series):
    idx = y[x.lt(400)].index[0]
    max = y.iloc[:idx].max()
    return max


#### Paths
paths = args.files
labels = args.labels
hasLabels = len(labels) != 0
normalize = not args.nonorm
df = pd.DataFrame()
for file in paths:
    df = pd.concat([df, (pd.read_csv(file, header=1, usecols=[0,1]))], axis=1)

num_spc = int(df.shape[1])
gmax = 0 #global max
fig,ax = plt.subplots()
for i in range(0, num_spc,2):
    x = df.iloc[:,i]
    y = df.iloc[:,i+1]
    if normalize:
        # normalize
        max = getMax(y)
        y = y/max

    max = getMax(y)
    if(max >gmax): gmax = max
    if(not hasLabels or int(i/2) >= len(labels)):
        plt.plot(x,y)
    else:
        plt.plot(x,y,label=labels[int(i/2)])

ax.legend()
ax.tick_params(direction="out", top=False, right=False) 
ax.tick_params(which="minor", axis="y", right=False,direction="out")
ax.tick_params(which="minor", axis="x", top=False, direction="out")

def forward(x):
    return 1e4/x

def inverse(x):
    return 1e4/x

secax = ax.secondary_xaxis('top', functions=(forward, inverse))
secax.xaxis.set_minor_locator(AutoMinorLocator(2))
secax.set_xlabel("$\mathregular{\\nu}$ /$\mathregular{10^3}$$\mathregular{cm^{-1}}$")
ax.set_xlim(250, 1100)
ax.set_ylim(0, gmax + 0.1*gmax)
ax.set_xlabel("$\mathregular{\lambda}$ /nm")
ax.set_ylabel("norm. Abs.")
plt.savefig("out/img.png", dpi=1200)