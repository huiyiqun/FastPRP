from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name='FastPRP',
    version='0.0.1',
    description='Impelemtation of the Fast Pseudo-Random Permutations.',
    ext_modules=cythonize("FastPRP/convert.pyx"),
    packages=find_packages(),
    author='Hui Yiqun',
    author_email='huiyiqun@gmail.com',
    url='https://github.com/huiyiqun/FastPRP',
    install_requires=['pycrypto'],
    license='GPL',
)
