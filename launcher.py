#!/usr/bin/env python3
import sys

# check if using python 3.5+
if sys.version_info >= (3, 5):
    import Discline
    Discline.main()
else:
    print("Sorry, but this requires python 3.5+")
    quit()

