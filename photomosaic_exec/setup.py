"""
setup.py

PURPOSE:
    Build script for all Cython and C extensions used in the PhotoMosaic project.
    Compiles photomosaic engine modules for performance.

HOW TO USE:
    From the photomosaic_exec/ directory, run:
        python setup.py build_ext --inplace

REQUIREMENTS:
    - Python (ideally Python 3, but supports 2.7 legacy)
    - numpy
    - Cython
    - distutils

MODERNIZATION NOTES:
    - For Python 3: ensure print syntax, absolute imports, and Cythonize as needed.
    - For new projects, consider using setuptools instead of distutils.
    - Compatible with current project layout (color_metrics/ as a subfolder of PhotoMosaic_source).

OUTPUT:
    Compiled .so/.pyd modules in the current directory for import by the main app.

Author: MozayLab Project
"""

import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("photomosaic", ["photomosaic.py"],
              include_dirs=[numpy.get_include(), "."],
              library_dirs=[],
              libraries=[]),
    Extension("jigsaw", ["jigsaw.py"],
              include_dirs=[numpy.get_include(), "."],
              library_dirs=[],
              libraries=[]),
    Extension("directory_walker", ["directory_walker.py"],
              include_dirs=["."],
              library_dirs=[],
              libraries=[]),
    Extension("memo", ["memo.py"],
              include_dirs=["."],
              library_dirs=[],
              libraries=[]),
    Extension("progress_bar", ["progress_bar.py"],
              include_dirs=["."],
              library_dirs=[],
              libraries=[]),
    Extension("color_metrics", [
        "PhotoMosaic_source/color_metrics/color_metrics.pyx",
        "PhotoMosaic_source/color_metrics/deltaE2000.c",
        "PhotoMosaic_source/color_metrics/rgb2lab.c"
    ],
    include_dirs=[numpy.get_include(), "."],
    library_dirs=[],
    libraries=[]),
    # Example for linking external C library:
    # Extension("integrate_mymath", ["integrate_mymath.pyx"],
    #           include_dirs=['.'],
    #           library_dirs=['.'],
    #           libraries=['mymath']),
]

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
)
