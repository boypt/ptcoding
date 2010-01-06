from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


setup (
        cmdclass = {'build_ext': build_ext},
        ext_modules = [
            Extension("looptest", ["cy_loop.pyx", "c_loop.c"],
                include_dirs=["/usr/include"],
                library_dirs=["/usr/lib"],
                libraries=[]
                )
            ]
        )
