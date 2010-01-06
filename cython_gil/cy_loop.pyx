
cdef extern from *:
    unsigned int sleep(unsigned int seconds) nogil #no NEED for GIL,
    int printf(char *format, ...) nogil # we are from C library!

cdef extern:
    void _c_loop() nogil # I don't need gil too, I'm of pure C!
    int end

def c_loop():
    with nogil: # don't take the GIL with me !
        _c_loop()

def cy_loop():
    global end
    with nogil:  # don't take the GIL with us !
        while not end:
            printf("Print from Cython loop\n")
            sleep(1)
    print "Cython loop ENDED"

def set_end(e):
    """Tell those C Threads to leave ... or they won't !"""
    global end
    end = e
