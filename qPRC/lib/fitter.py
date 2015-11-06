"""Fitting a model of the data concentrations"""

import numpy as np
import math
from scipy.optimize import curve_fit

def slice(concentrations_raw):
    """slice automatically"""
    conc_diff = concentrations_raw.diff()
    decrease_start_index = conc_diff[conc_diff<0].index[0]
    concentrations_series = concentrations_raw[: decrease_start_index - 1]
    concentrations = concentrations_series.values
    return concentrations

def f(meas, offset, n0, gama, nn, alfa):
    meas_calc = np.zeros(len(meas))
    for i in meas:
        num = np.zeros(i)
        prim = np.zeros(i)
        if n0 < 0 or nn < 0:
            return np.repeat(1e10, len(meas))
        num[0] = n0
        summ = n0
        prim[0] = nn
        for idx in range(1, i):
            num[idx] = num[idx - 1] * (
                1.0 + gama / (1.0 + alfa * (summ / prim[idx - 1]))
            )
            summ = summ + num[idx]
            prim[idx] = prim[idx - 1] - (num[idx] - num[idx - 1])

        meas_calc[i - 1] = num[-1] + offset
    return meas_calc

def fit(data, well, dye):
    """return the fitted model of the concentrations"""

    # select the concentrations column from the dataset
    concentrations_raw = data.loc[:,(well, dye)]
    concentrations = slice(concentrations_raw)

    # parameters - TODO: move to settings file or expose in the UI
    k = 1
    n = 5
    nx = 1
    nc = 5
    mode = 0
    maxit = 100000
    iprt = 0

    # offset
    offset = np.mean(concentrations[5:8])

    # expression
    last_reading = concentrations[-1]
    index = np.where((concentrations - offset) > 0.1 * last_reading)[0][0]
    expression = ((concentrations[index] - offset) /
                  math.exp(math.log(2.0)*index*1.0))

    # rate
    rate = 1.0

    # reactants
    reactants = last_reading/2.0

    # multiplier
    power = 1.0

    sy = concentrations.copy()
    for i, elm in enumerate(concentrations):
        if (elm > 1.5 * offset) and (elm < 0.5 * last_reading):
            sy[i] = 0.5
        elif (i < index - 10):
            sy[i] = 1.0
        elif (elm > last_reading/1.5):
            sy[i] = 1.5

    # bounds
    al = 0.0

    # these were from the old model
    # variables = np.array([5*offset, last_reading, 1.01,
    #                       last_reading + 10.0, 3.0])

    # obtained by randomly tweaking the output params and passing them into the
    # curve_fit again
    good_variables = [1.76050783e+05, 5.78e+02, +1.13766225e+00,
                      7.42308865e+05, 8.11068606e+00]

    times = list(range(1, len(concentrations) + 1))
    fitted_params = curve_fit(f, times, concentrations, p0=good_variables)
    params = fitted_params[0]
    return params
