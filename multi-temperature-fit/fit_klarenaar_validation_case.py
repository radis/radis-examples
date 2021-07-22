# -*- coding: utf-8 -*-
"""

Summary
-------

A 3 temperature fitting example reproducing the validation case of Klarenaar 2017 [1]_, who calculated a transmittance
spectrum from the initial data of Dang 1973 [2]_, with a 1 rotational temperature +
3 vibrational temperature (Treanor distributions) model

CO2 Energies are calculated from Dunham developments in an uncoupled harmonic
oscillator - rigid rotor model

.. image:: docs/multi-temperature-fit.gif

The example is based on one of `RADIS validation cases <https://github.com/radis/radis/tree/master/radis/test/validation>`_.

It makes use of the RADIS `Spectrum <file:///D:/GitHub/radis/docs/_build/html/index.html#the-spectrum-class>`_
class and the associated compare and load functions


References
----------

.. [1] Klarenaar et al 2017, "Time evolution of vibrational temperatures in a CO2 glow
       discharge measured with infrared absorption spectroscopy"

.. [2] Dang et al 1973, "Detailed vibrational population distributions in a CO2 laser
        discharge as measured with a tunable diode laser"

"""

from radis.test.utils import getValidationCase
from radis import SpectrumFactory, Spectrum
from radis.spectrum.compare import get_residual
from radis.spectrum import plot_diff
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from os.path import join

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#                 USER SECTION    (change this as you want)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# %% Get Fitted Data

# Data from Dang, adapted by Klarenaar, digitized by us
s_exp = Spectrum.from_txt(getValidationCase(join('test_CO2_3Tvib_vs_klarenaar_data',
                                                 'klarenaar_2017_digitized_data.csv')),
                          'transmittance_noslit', waveunit='cm-1', unit='',
                          delimiter=',',
                          name='Klarenaar 2017')

w_exp, T_exp = s_exp.get('transmittance_noslit', wunit='cm-1')

# %% Calculate

sf = SpectrumFactory(2284.2, 2284.6,
                     wstep=0.001,                # cm-1
                     pressure=20*1e-3,           # bar
                     db_use_cached=True,
                     lvl_use_cached=True,
                     cutoff=1e-25,
                     isotope='1,2',
                     path_length=10,             # cm-1
                     mole_fraction=0.1*28.97/44.07,
                     broadening_max_width=1,     # cm-1
                     medium='vacuum',
                     export_populations=None,   # 'vib',
                     )
sf.warnings['MissingSelfBroadeningWarning'] = 'ignore'
sf.load_databank('HITEMP-CO2-TEST')

# Get initial values of fitted parameters
model_input = {'T12':517,
               'T3':2641,
               'Trot':491,
               }

# Calculate a new spectrum for given parameters:
def theoretical_model(model_input):
    ''' Returns a Spectrum for given inputs T

    Parameters
    ----------

    model_input: dict
        input dictionary (typically: temperatures)

    Returns
    -------

    s: :class:`~radis.spectrum.spectrum.Spectrum`
        calculated Spectrum

    '''

    # ... input should remain a dict
    T12 = model_input['T12']
    T3 = model_input['T3']
    Trot = model_input['Trot']

    # ... create whatever model below (can have several slabs with SerialSlabs
    # ... or MergeSlabs, etc.)

    # >>> This is where the RADIS calculation is done!

    s = sf.non_eq_spectrum((T12, T12, T3), Trot, Ttrans=Trot,
                           vib_distribution='treanor',
                           name='treanor. fit')

    # <<<

    # ... output should be a Spectrum object
    return s

# Calculate initial Spectrum, by showing all steps.
sf.verbose=3    # increase verbose level for more details.
theoretical_model(model_input).plot('transmittance_noslit', nfig='Initial spectrum')
sf.verbose=0    # reduce verbose during calculation.

# %% Leastsq version

# %%
# User Params
# -----------

#T0 = 1000
fit_params = ['T12', 'T3', 'Trot']
bounds = np.array([[300, 2000],
                   [300, 5000],
                   [300, 2000]])
fit_units = ['K', 'K', 'K']
fit_variable = 'transmittance_noslit'




# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#                 FITTING MACHINERY    (you shouldnt need to edit this)
#                  ... just a few functions to make nice plots along
#                  ... the fitting procedure
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# %%
# Algorithm Params
# ----------------

history_x = []
history_res = []
maxiter = 300

def print_fit_values(fit_values):
    return ','.join(['{0}={1}{2}'.format(
                fit_params[i], np.round(fit_values[i], 0), fit_units[i])
                for i in range(len(fit_params))])

def generate_spectrum(fit_values):


        # Generate dictionary
        inputs = model_input.copy()
        for k, v in zip(fit_params, fit_values):
            inputs[k] = v

        # Calculate the theoretical model
        s = theoretical_model(inputs)

        return s


def cost_function(fit_values, plot=None):
    ''' Return error on Spectrum s vs experimental spectrum'''

    s = generate_spectrum(fit_values)

    # Delete unecessary variables (for a faster resampling)
    for var in [k for k in s._q.keys() if k not in [fit_variable, 'wavespace']]:
        del s._q[var]

    if plot is not None:
        plt.figure(plot).clear()
        plot_diff(s_exp, s, var=fit_variable, nfig=plot, title=print_fit_values(fit_values))

    s.resample(w_exp, energy_threshold=2e-2)

    return get_residual(s, s_exp, fit_variable, ignore_nan=True, norm='L2')


def log_cost_function(fit_values, plot=None):
    ''' Calls the cost_function, and write the values to the Log history  '''

    res = cost_function(fit_values, plot=plot)

    history_x.append(fit_values)
    history_res.append(res)

    return res

# Graph with plot diff
figSpec, axSpec = plt.subplots(num='diffspectra')


# Graph with residual
# ... unlike 1D we cant plot the temperature here. Just plot the iteration

plt.close('residual')
figRes, axRes = plt.subplots(num='residual', figsize=(13.25, 6))
axValues = axRes.twinx()
#ax = fig.gca()
#ax.set_ylim((bounds[0]))

fit_values_min, fit_values_max = bounds.T
res0 = log_cost_function(fit_values_min)
res1 = log_cost_function(fit_values_max, plot=figSpec.get_label())
lineRes, = axRes.plot((1, 2), (res0, res1), '-ko')
lineLast, = axRes.plot(2, res0, 'or')          # last iteration in red
lineValues = {}
for i, k in enumerate(fit_params):
    lineValues[k] = axValues.plot((1, 2), (fit_values_min[i], fit_values_max[i]), '-', label=k)[0]
axRes.set_xlim((0, maxiter))
axRes.set_ylim(ymin=0)
axRes.set_xlabel('Iteration')
axRes.set_ylabel('Residual')
figRes.legend()
sf.verbose = False
sf.warnings['NegativeEnergiesWarning'] = 'ignore'

ite = 2
plot_every = 1   # plot spectra every # iterations

def cost_and_plot_function(fit_values):
    ''' Return error on Spectrum s vs experimental spectrum

    This is the function that is called by minimize() '''
    global ite
    ite += 1
    # Plot one spectrum every 10 ites
    plot = None
    if not ite % plot_every:
        plot=figSpec.get_label()

    res = log_cost_function(fit_values, plot=plot)

    # Add to plot history
    x, y = lineRes.get_data()
    lineRes.set_data((np.hstack((x, ite)),
                      np.hstack((y, res))))
    # Add values to history
    for k, v in zip(fit_params, fit_values):
        x, y = lineValues[k].get_data()
        lineValues[k].set_data((np.hstack((x, ite)),
                                np.hstack((y, v))))
    # Plot last
    lineLast.set_data((ite, res))

    figRes.canvas.draw()
    plt.pause(0.01)

    print('{0}, Residual: {1:.4f}'.format(print_fit_values(fit_values), res), flush=True)

    return res

# >>> This is where the fitting loop happens
print('\nNow starting the fitting process:')
print('---------------------------------\n')
best = minimize(cost_and_plot_function, (fit_values_max+fit_values_min)/2,
#                method='L-BFGS-B',
                method='TNC',
                jac=None,
                bounds=bounds,
                options={'maxiter' : maxiter,
                         'eps':20,
#                         'ftol':1e-10,
#                         'gtol':1e-10,
                         'disp':True})
# <<<

s_best = generate_spectrum(best.x)

if best.success:
    print('Final {0}: {1}{2}'.format(fit_params, np.round(best.x), fit_units))

# Res history

# ... what does history say:
print('Best: {0}: {1}{2} reached at iteration {3}/{4}'.format(
                    fit_params,
                    history_x[np.argmin(history_res)],
                    fit_units,
                    np.argmin(history_res),
                    best.nfev))

# ... note that there are more function evaluations (best.nfev) that actual solver
# ... iterations (best.nit) because the Jacobian is calculated numerically with
# ... internal function calls

