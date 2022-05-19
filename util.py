from matplotlib.ticker import AutoMinorLocator
import pandas as pd


def forward(x):
    return 1e4/x


def inverse(x):
    return 1e4/x


def applyAxisSettings(ax, gmax, normalize):
    ax.legend()
    ax.tick_params(direction="out", top=False, right=False)
    ax.tick_params(which="minor", axis="y", right=False, direction="out")
    ax.tick_params(which="minor", axis="x", top=False, direction="out")
    secax = ax.secondary_xaxis('top', functions=(forward, inverse))
    secax.xaxis.set_minor_locator(AutoMinorLocator(2))
    secax.set_xlabel("$\mathregular{\\nu}$ /$\mathregular{10^3}$$\mathregular{cm^{-1}}$")
    ax.set_xlim(250, 1100)
    ax.set_ylim(0, gmax + 0.1*gmax)
    ax.set_xlabel("$\mathregular{\lambda}$ /nm")
    if normalize:
        ax.set_ylabel("norm. Abs.")
    else:
        ax.set_ylabel("rel. Abs.")
