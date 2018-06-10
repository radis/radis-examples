==============
RADIS Examples
==============

This project includes:

- Interactive examples to calculate infrared spectra of molecules with `RADIS <http://radis.readthedocs.io/>`__

- Static examples of fitting algorithm built around `RADIS <http://radis.readthedocs.io/>`__

Interactive Examples
--------------------

Run RADIS interactively directly from the browser. No installation needed!

.. image:: https://mybinder.org/badge.svg 
    :target: https://mybinder.org/v2/gh/radis/radis-examples/master?filepath=spectrum.ipynb
    :alt: Binder


Static Examples
---------------

`Install RADIS <https://radis.readthedocs.io/en/latest/install.html#install>`_ 
then run these examples locally. 


multi-temperature-fit
~~~~~~~~~~~~~~~~~~~~~

A 3 temperature fitting example reproducing the validation case of Klarenaar 2017 [1]_, who calculated a transmittance
spectrum from the initial data of Dang 1973 [2]_, with a 1 rotational temperature + 
3 vibrational temperature (Treanor distributions) model 

CO2 Energies are calculated from Dunham developments in an uncoupled harmonic 
oscillator - rigid rotor model

.. image:: docs/multi-temperature-fit.gif

The example is based on one of `RADIS validation cases <https://github.com/radis/radis/tree/master/radis/test/validation>`_.

It makes use of the RADIS `Spectrum <file:///D:/GitHub/radis/docs/_build/html/index.html#the-spectrum-class>`_
class and the associated compare and load functions


Links
-----

- RADIS Documentation: http://radis.readthedocs.io/
- RADIS Source files: https://github.com/radis/radis
- PyPi project: https://pypi.python.org/pypi/radis
- Test status: https://travis-ci.org/radis/radis
- Test coverage: https://codecov.io/gh/radis/radis


References
----------

.. [1] Klarenaar et al 2017, "Time evolution of vibrational temperatures in a CO2 glow 
       discharge measured with infrared absorption spectroscopy"

.. [2] Dang et al 1973, "Detailed vibrational population distributions in a CO2 laser 
        discharge as measured with a tunable diode laser"
