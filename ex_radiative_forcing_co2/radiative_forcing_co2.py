# -*- coding: utf-8 -*-
"""
Calculates the upward-radiation for different CO2 mole fractions in the atmosphere.

Atmosphere is calculated from the [Standard Atmosphere]_ profiles of pressure
and temperature. CO2 mole fraction is assumed homogeneous. 


Notes
-----

Line-of-sight: RADIS has a very simple 1D line-of-sight model assuming
a cylindrical column of air

For comparison, [MODTRAN]_ "computes line-of-sight (LOS) radiances by integrating 
through a stratified spherical atmosphere, including the effects of light refraction.
Multiple scattering contributions are most accurately computed using the plane 
parallel atmosphere DISORT discrete ordinate model."

References
---------

.. [MODTRAN] http://modtran.spectral.com/modtran_features#lbl

.. [Standard Atmosphere] https://www.digitaldutch.com/atmoscalc/tableatmosphere.htm


"""

from __future__ import print_function, absolute_import, division

from radis import SpectrumFactory, sPlanck, SerialSlabs
import matplotlib.pyplot as plt
import pandas as pd
from numpy import pi
from radis.misc.progress_bar import ProgressBar
from radis import cm2nm
from radis.misc import centered_diff
from publib import set_style, fix_style


#%% ===========================================================================
# Read Data and get Inputs
# =============================================================================

SAVE_OUTPUT = True

#%% Read atmosphere data
atm = pd.read_csv(r'data/atmosphere_standard_profile_1976.csv', comment='#')
atm['path_length'] = centered_diff(atm.z_km)   

#%% Plot atmosphere data
set_style('origin')
fig, ax = plt.subplots()
ax.plot(atm.P_Pa*1e-5, atm.z_km)
ax.set_xlabel('Pressure [bar]')
ax.set_ylabel('Altitude [km]')

ax2 = ax.twiny()
ax2.plot(atm.T_K, atm.z_km, 'r')
ax2.set_xlabel('Temperature [K]', color='r')
ax2.tick_params('x', colors='r')

plt.tight_layout()
fix_style('origin') 

if SAVE_OUTPUT:
    from radis.misc import make_folders
    make_folders('.', ['out'])
    plt.savefig('out/atmosphere_standard_profile_1976.pdf')    
    plt.savefig('out/atmosphere_standard_profile_1976.png')    


# %% Atmosphere Parameters

# Physical parameters                  
wmin = 400                       #: wavenumber min
wmax = 900                       #: wavenumber max
x_CO2 = 400e-6     #: float: mole fraction of CO2 

# Spectral Computation parameters
wstep = 0.003                    # wavenumber step (cm-1)
broadening_max_width = 3         # Line broadening (cm-1)

# %% Earth Model
# without albedo, but lower effective temperature 
albedo = 0        # reflectivity of the earth surface
T_earth = 288     # average night/day Earth surface  K 

# %% Get Spectral line database
sf = SpectrumFactory(wavenum_min=wmin, 
                     wavenum_max=wmax,
                     molecule='CO2',
                     isotope='1,2,3',
                     verbose=False,
                     broadening_max_width=broadening_max_width,
                     wstep=wstep,
                     warnings={'MissingSelfBroadeningWarning':'ignore'},
                     export_lines=False,
                     chunksize='DLM',
                     )
sf.fetch_databank(load_energies=False)   # loads from HITRAN, requires an internet connection


#%% ===========================================================================
# Calculations
# =============================================================================

# Calculate ground emission
s_earth_0 = sPlanck(wmin, wmax, wstep=wstep, T=T_earth, eps=1-albedo)


#%% Calculate atmosphere

# Calculate atmosphere layers

slabs = []
print('Calculating Atmosphere layers')
pb = ProgressBar(len(atm))
for i, r in atm.iterrows():
    pb.update(i)
    s = sf.eq_spectrum(Tgas=r.T_K,
                       mole_fraction=x_CO2,
                       path_length=r.path_length*1e5, # cm
                       pressure=r.P_Pa*1e-5, # bar
                       )
    slabs.append(s)
pb.done()
    
# now solve the line of sight for the atmosphere:
print('Solving radiative transfer equation')
s_atm = SerialSlabs(*slabs)

# %% Calculate the total Upward radiation

s_los_400 = SerialSlabs(s_earth_0, s_atm, resample='intersect')

# Note: RADIS does not have an irradiance unit by default. 
# Here we create the irradiance from the radiance 
s_los_400._q['irradiance'] = s_los_400.get('radiance_noslit')[1]*pi
s_los_400.units['irradiance'] = s_los_400.units['radiance_noslit'].replace('/sr', '')
s_los_400.name = 'Earth + Atmosphere'

# %% Rescale to 1750 reference (278 ppm)
'''
Note
----

rescaling a preexisting spectrum with different mole fractions neglects 
the change in the broadening of the line shape. For more accurate calculations
you may want to recalculate the atmosphere entirely (commented lines, below)
and compare
'''

x_CO2_ref = 278e-6 

slabs_278 = []
print('Calculating Reference Atmosphere')
pb = ProgressBar(len(atm))
for i, r in atm.iterrows():
    pb.update(i)
    # 1. Rescale existing (see Note above):
    s = slabs[i].copy()
    s.rescale_mole_fraction(x_CO2_ref)
    # 2. Or recalculate:
#    s = sf.eq_spectrum(Tgas=r.T_K,
#                       mole_fraction=x_CO2_ref,
#                       path_length=r.path_length*1e5, # cm
#                       pressure=r.P_Pa*1e-5, # bar
#                       )
    
    slabs_278.append(s)
pb.done()

# now solve the line of sight for the atmosphere:
print('Solving radiative transfer equation')
s_atm_278 = SerialSlabs(*slabs_278)
    
#%% Now Upward radiation

# now solve the line of sight: 
s_atm_278 = SerialSlabs(*slabs_278)
    
# %% Calculate the total Upward radiation
s_los_278 = SerialSlabs(s_earth_0, s_atm_278, resample='intersect')

# Note: RADIS does not have an irradiance unit by default. 
# Here we create the irradiance from the radiance 
s_los_278._q['irradiance'] = s_los_278.get('radiance_noslit')[1]*pi
s_los_278.units['irradiance'] = s_los_278.units['radiance_noslit'].replace('/sr', '')
s_los_278.name = 'Earth + Atmosphere'




#%% ===========================================================================
# Post Processing
# =============================================================================

from radis.spectrum.utils import make_up    # to print units nicer

# %% Plot comparison of 278ppm vs 400 ppm
# Ajust as you want!
Iunit = 'W/m2/nm'

# Reduce the range (for nicer graph)
s_los_278.crop(wmin=11100, wmax=20000, wunit='nm')
s_los_400.crop(wmin=11100, wmax=20000, wunit='nm')

# Get total power in this range
P_278 = s_los_278.get_integral('irradiance', wunit='nm', Iunit='W/m2/nm')
P_400 = s_los_400.get_integral('irradiance', wunit='nm', Iunit='W/m2/nm')

print('Upward radiation @278 ppm: {0:.1f} W/m2'.format(P_278))
print('Upward radiation @400 ppm: {0:.1f} W/m2'.format(P_400))

s_los_278.name = '278 ppm: {0:.1f} W/m2'.format(P_278)
s_los_400.name = '400 ppm: {0:.1f} W/m2'.format(P_400)

# Plot
s_los_278.plot('irradiance', wunit='nm', Iunit=Iunit) #cm_1')
s_los_400.plot('irradiance', wunit='nm', Iunit=Iunit, nfig='same', zorder=-1) #/cm_1
plt.ylim(ymin=0)
plt.legend(loc='best')
plt.tight_layout()

# Add some Planck lines every 20 K
for T_planck in [200, 220, 240, 260, 280, 300, 320]:
    s_planck = sPlanck(wavelength_min=11100, 
                       wavelength_max=20000, 
                       wstep=10, T=T_planck, eps=1)
    # Note: RADIS does not have an irradiance unit by default. 
    # Here we create the irradiance from the radiance 
    s_planck._q['irradiance'] = s_planck.get('radiance_noslit')[1]*pi
    s_planck.units['irradiance'] = s_planck.units['radiance_noslit'].replace('/sr', '')
    s_planck.plot('irradiance', wunit='nm', Iunit='W/m2/nm', nfig='same', color='lightgrey', ls='--', zorder=-10)

plt.grid(False)
plt.ylabel('Irradiance ({0})'.format(make_up(Iunit)))

if SAVE_OUTPUT:
    plt.savefig('out/atmosphere_co2_column.pdf')
    plt.savefig('out/atmosphere_co2_column.png')



# %% Below we calculate the upward radiation for different altitudes
# Helps see the different layers of atmosphere

plt.figure()
for km in [1, 5, 10, 20, 60]:

    SerialSlabs(s_earth_0, *slabs[:km]).plot(Iunit='W/m2/sr/nm', nfig='same', label='{0} km'.format(km))
plt.legend()

#%% ... Print

print('Upward radiation @278 ppm: {0:.1f} W/m2'.format(s_los_278.get_integral('irradiance', wunit='nm', Iunit='W/m2/nm')))
print('Upward radiation @400 ppm: {0:.1f} W/m2'.format(s_los_400.get_integral('irradiance', wunit='nm', Iunit='W/m2/nm')))
