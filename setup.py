from setuptools import setup
from sys import platform

with open('README.rst') as README:
    long_description = README.read()
    description = long_description[:long_description.index('Description')].split("*")[1].strip()
    long_description = long_description[long_description.index('Description'):]

setup(
      name='a2p2',
      version='0.0.1',
      description=description,
      long_description=long_description,
      #      install_requires=['astropy', 'p2api','pygtk'],
      # PyGtk is not working on some linux
      # anaconda also fails 
      # prefere the use of your default python packages on your linux
      # what is the solution for mac ?
      install_requires=['astropy', 'p2api'] + (['pygtk'] if platform.startswith("win") else []),
      url='http://www.jmmc.fr/a2p2',
      author='JMMC Tech Group',
      author_email='jmmc-tech-group@jmmc.fr',
      classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
      ],
      license='OSI Approved :: GNU General Public License v3 (GPLv3)',
      packages=['a2p2'],
      scripts=['scripts/a2p2'],
      keywords='observation preparation tool optical-interferometry p2 samp'
      )
