#!/bin/bash

(sed 's/^python.\+$/python << EOF/' blog-dev.vim; cat blog.py) > blog.vim


