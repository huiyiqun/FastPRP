Description
===========

1. Impelemtation of the Fast Pseudo-Random Permutations.

  Inspired by [this paper](https://eprint.iacr.org/2012/254.pdf)


How To
======

1. Compile the cython module

    python setup.py build_ext --inplace

or simply use python

    cp convert.pyx convert.py

2. There is two modules in my project now:

  * `RandomPermute` in RandomPermute.py (aimed to cryptology-safe)
  * `ArbitaryWidthRandomPermute` in ArbitaryWidthRandomPermute.py

test units for either module is in the source code. just run it:

    python RandomPermute.py
    python ArbitaryWidthRandomPermute.py

TODO
====

1. There is not tutorist. Just see the source code.
