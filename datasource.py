import fnmatch
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from natsort import humansorted

from settings import colorMap

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
    soret:float = 0
    max: float = 0

    def __init__(self, folder: str, mass: float, molar: float, tfa: float):
        self.folder = folder
        self.mass = mass  # weight of substance
        self.molar = molar  # molar mass of substance
        self.tfa = tfa  # mL conc tfa used
        self.nTfa = self.tfa*rTfa/MTfa  # mol
        self.npVTfa = self.nTfa/self.vTfa  # mol/mL
        self.initialMoles = self.mass/1000/self.molar
        self.moles = self.initialMoles*self.usedPart

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
        idx = corr[corr.iloc[:,0].lt(400.0)].index[0]
        soret = corr.iloc[:idx, 1].idxmax()
        self.soret = soret

        for i in range(0, num_spc, 2):
            fac = self.moles/(((i/2)+50)/1000)
            corr.iloc[:,i+1] = corr.iloc[:,i+1]/fac
            if max < corr.iloc[:,i+1][soret]:
                max = corr.iloc[:,i+1][soret]
        self.max = max
        return corr
    def plot(self, corr: pd.DataFrame):
        num_spc = int(corr.shape[1])
        cols = colorMap(num_spc)
        fig,ax = plt.subplots()
        for i in range(0, num_spc, 2):
            x = corr.iloc[:,i]
            y = corr.iloc[:,i+1]
            plt.plot(x,y, color=cols[int(i/2)])
        ax.set_xlim(250,1100)
        ax.set_ylim(0, self.max + 0.1*self.max)
        ax.set_xlabel("$\mathregular{\lambda}$ /nm")
        ax.set_ylabel("$\mathregular{\epsilon}$ /$\mathregular{L mol^{-1}cm^{-1}}$")
        plt.savefig("out/titration.png", dpi=1200)

    def calculatePH(self, corr: pd.DataFrame) -> float:
        sorets_y= corr.iloc[self.soret].iloc[1::2]
        # drop first two entries
        x_mlTFA = np.arange(0, len(sorets_y), 1)
        x_V = 50 + x_mlTFA
        x_nTFA =  x_mlTFA * self.npVTfa
        x_cTFA = x_nTFA/x_V
        x = -np.log10(x_cTFA)
        x = x[:-1]
        sorets_y = sorets_y[:-1]
        x= 0.443141*np.exp((x-3.27759)/1.09351) # correction with calculated fit to pH
        der = np.gradient(sorets_y,x) # derivate
        min = np.nanargmin(der) # minimum

        fig, ax = plt.subplots()
        ax.set_xlabel("pH")
        ax.set_ylabel("$\mathregular{\epsilon}$ /$\mathregular{L mol^{-1}cm^{-1}}$")
        plt.plot(x, sorets_y)
        plt.scatter(x[min], sorets_y[min])
        plt.annotate(np.round(x[min],2),xy=(x[min], sorets_y[min]), textcoords="offset points", xytext=(5,0), fontsize=9)
        return x[min]