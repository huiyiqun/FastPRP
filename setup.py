from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Fast bytes to list of bools',
  ext_modules = cythonize("bytes2bools.pyx"),
)
