import fnmatch
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from natsort import humansorted
from scipy.signal import savgol_filter
from settings import colorMap
from util import applyAxisSettings

# constants
MTfa = 114.02  # g/mol, molar mass of TFA
rTfa = 1.48  # g/mL, density of TFA


class DataSource:
    usedPart: float = 1/5  # amount taken from initial
    volume: float = 50  # mL
    vTfa: float = 50  # ml
    nTfa: float
    npVTfa: float
    initialMoles: float
    moles: float
    soret: float = 0
    q: float = 0
    max: float = 0

    def __init__(self, folder: str, mass: float, molar: float, tfa: float, vTfa: float = 50):
        self.folder = folder
        self.mass = mass  # weight of substance
        self.molar = molar  # molar mass of substance
        self.tfa = tfa  # mL conc tfa used
        self.nTfa = self.tfa*rTfa/MTfa  # mol
        self.npVTfa = self.nTfa/self.vTfa  # mol/mL
        self.initialMoles = self.mass/1000/self.molar
        self.moles = self.initialMoles*self.usedPart
        self.vTfa = vTfa

    def loadData(self) -> pd.DataFrame:
        data = []
        for root, dir, files in os.walk(self.folder):
            for file in fnmatch.filter(files, "*.csv"):
                data.append(os.path.join(root, file))
        data = humansorted(data)
        df = pd.DataFrame()
        for item in data:
            df = pd.concat([df, (pd.read_csv(item, header=1, usecols=[0, 1]))], axis=1)
        return df

    def calculateCorrection(self, df: pd.DataFrame):
        num_spc = int(df.shape[1])
        corr = df.copy(deep=True)
        max = 0
        idx = corr[corr.iloc[:, 2].lt(400.0)].index[0]
        idx2 = corr[corr.iloc[:, 2].lt(800.0)].index[0]
        self.q = corr.iloc[:idx2, 1].idxmax()
        soret = corr.iloc[:idx, 1].idxmax()
        self.soret = soret

        for i in range(0, num_spc, 2):
            fac = self.moles/(((i/2)+50)/1000)
            corr.iloc[:, i+1] = corr.iloc[:, i+1]/fac
            if max < corr.iloc[:, i+1][soret]:
                max = corr.iloc[:, i+1][soret]
            
        self.max = max
        return corr

    def plot(self, corr: pd.DataFrame):
        num_spc = int(corr.shape[1])
        cols = colorMap(num_spc)
        fig, ax = plt.subplots()
        for i in range(0, num_spc, 2):
            x = corr.iloc[:, i]
            y = corr.iloc[:, i+1]
            plt.plot(x, y, color=cols[int(i/2)])
        applyAxisSettings(ax, self.max, False)
        ax.set_ylabel("$\mathregular{\epsilon}$ /$\mathregular{L mol^{-1}cm^{-1}}$")
        plt.savefig("out/titration.png", dpi=1200)
        plt.savefig("out/titration.svg", dpi=1200)
        return fig, ax

    def calculatePH(self, corr: pd.DataFrame, idx: int, offset: int = 0, usePH = True) -> float:
        sorets_y = corr.iloc[idx].iloc[1::2]
        # drop first two entries
        x_mlTFA = np.arange(0, len(sorets_y), 1)
        x_V = (50 + x_mlTFA) /1000 # L
        x_nTFA = x_mlTFA * self.npVTfa # ml * mol/mL
        x_cTFA = x_nTFA/x_V # mol/L
        print(x_cTFA)
        x = -np.log10(x_cTFA)
        x = x[:-1]
        sorets_y = sorets_y[:-1]
        lol = len(x)
        if(lol % 2 == 0):
            lol = lol-1
        sorets_y_sm = savgol_filter(sorets_y, lol, 4)  # smooth
        if usePH: x = 0.364+0.03822*np.exp((x+0.68451)/1.20156)  # correction with calculated fit to pH
        fig, ax = plt.subplots()
        if usePH: ax.set_xlabel("pH")
        else: ax.set_xlabel("-log[TFA]")
        ax.set_ylabel("$\mathregular{\epsilon}$ /$\mathregular{L mol^{-1}cm^{-1}}$")
        plt.plot(x, sorets_y, label="data")
        plt.plot(x, sorets_y_sm, label="smoothed data")
        der = np.gradient(sorets_y_sm, x)
        der2 = np.gradient(der, x)
        idx = np.where(np.diff(np.sign(der2[~np.isnan(der2)])))[0][-1-offset]
        y = sorets_y[idx]
        pt = x[idx]
        plt.scatter(pt, y)
        plt.annotate(np.round(pt, 2), xy=(pt, y), textcoords="offset points", xytext=(5, 0), fontsize=9)
        plt.savefig("out/pH.png", dpi=1200)
        plt.savefig("out/pH.svg", dpi=1200)
        return pt
