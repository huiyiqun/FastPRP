from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Fast tools to covert among uint, bytes and list of bools',
    ext_modules=cythonize("convert.pyx"),
)
