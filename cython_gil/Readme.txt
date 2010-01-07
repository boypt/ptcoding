1.to compile the module, run:

python setup build

and the module library will be generated in the build directory.

2.look into `build' to see, whether the path is same as it will be acquired in `py_test.py', if not, change the code.

sys.path.append("build/lib.linux-x86_64-2.6/") 
