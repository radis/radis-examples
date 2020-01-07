# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 11:04:35 2020

@author: erwan


Plot all HITRAN spectraat 300 K for the first isotope


"""

from radis import calc_spectrum, MOLECULES_LIST_EQUILIBRIUM
from radis.misc import ProgressBar, make_folders
import matplotlib.pyplot as plt

make_folders('.', 'out')
pb = ProgressBar(len(MOLECULES_LIST_EQUILIBRIUM))
for i, M in enumerate(MOLECULES_LIST_EQUILIBRIUM):
    pb.update(i)
    filename = 'out/{0} - {1} infrared spectrum.png'.format(i, M)
    
    # To skip the existing ones 
    from os.path import exists
    if exists(filename):
        continue
    
    try:
        # Calculate RADIS spectrum
        s = calc_spectrum(wavelength_min=1000, 
                          wavelength_max=20000,
                          Tgas=300,
                          pressure=1,
                          molecule=M,
                          lineshape_optimization=None,
                          cutoff=1e-23,
                          isotope='1',
                          verbose=0)
        
        # Plot and save it
        s.name=M.replace('2', '$_{2}$').replace('3', '$_{3}$').replace('4', '$_{4}$')
        s.name += ' ({0:.1f}s)'.format(s.conditions['calculation_time'])
        s.plot('abscoeff', wunit='nm')  # TODO: switch to µm after it's possible
        plt.yscale('log')
        plt.legend(loc='upper right')
        plt.savefig(filename)
        plt.close()
    except Exception as err:
        # Errors can occur: isotopes not defined, no lines in the range, etc... Here we just 
        # proceed to the next molecule 
        print('Error with {0}:'.format(M))
        print(err)
pb.done()