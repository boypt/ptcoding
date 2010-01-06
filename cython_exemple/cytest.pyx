
cdef extern from "cmodule.h":
    void say_hello()
    void show_args (int argc, char *argv[])

cdef extern from "stdlib.h":
    void *calloc(size_t nmemb, size_t size)
    void free(void *ptr)

def call_c_hello():
    say_hello()


def call_with_args(args):
    args_list = args.split();

    cdef char **argv
    cdef int argc = len(args_list) + 1

    argv = <char**>calloc(argc, sizeof(char*))

    argv[0] = "cytest"

    for i in range(1, argc):
        argv[i] = args_list[i-1]
    
    show_args(argc, argv)
    free(argv)

