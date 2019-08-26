
"""
An example that reproduces approximately the line-of-sight calculation of Fig. 9 in 
Pannier and Laux 2018, "Analysis of JAXA Nonequilibrium Infrared Emission Spectra for Mars Entry Conditions"

.. warning::

  the CO2 database used in the paper for the CO2 equilibrium case is CDSD-4000. 
  The database used below is HITEMP-2010, which makes calculations faster 
  for the sake of the example. Expect some differences in the > 4.4 µm region 

"""

from radis import SpectrumFactory, SerialSlabs

# Calculate CO2
sf = SpectrumFactory(wavelength_min=4000, 
                     wavelength_max=5000,                # cm-1
                     wstep=0.01,
                     isotope='1',
                     verbose=3,
                     chunksize='DLM',
                     )
sf.load_databank('HITEMP-CO2')  # link to my CO2 HITEMP database files
s_forebody = sf.eq_spectrum(Tgas=4000, pressure=1, mole_fraction=0.027, path_length=1)
s_freeflow = sf.non_eq_spectrum(Trot=1690, pressure=0.017, Tvib=2200, mole_fraction=0.606, path_length=3)

# Calcule CO
sfco = SpectrumFactory(wavelength_min=4000, 
                     wavelength_max=5000,                # cm-1
                     wstep=0.01,
                     isotope='1',
                     verbose=3,
                     )
sfco.load_databank('HITEMP-CO')    # link to my CO HITEMP database files
s_co = sfco.non_eq_spectrum(# non_eq_spectrum because eq_spectrum requires partitions functions 
                            # tabulated with TIPS which is limited to 3000 K 
                            Tvib=4000, Trot=4000, 
                            pressure=1, mole_fraction=0.519, path_length=1)  

# Combine
s = SerialSlabs(s_freeflow, s_forebody // s_co, s_freeflow)
s.apply_slit(10, 'nm')
s.plot(wunit='nm', Iunit='W/cm2/sr/um')
