from setuptools import setup, find_packages

INSTALL_REQUIRES = [
      'pandas',
      'requests',
      'yfinance',
      'finvizfinance',
]

setup(name = 'investor_watch', version='1.0', packages=find_packages())