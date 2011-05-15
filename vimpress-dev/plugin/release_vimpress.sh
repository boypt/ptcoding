#!/bin/bash

(sed '/^python/d' blog-dev.vim; cat blog.py) > blog.vim


