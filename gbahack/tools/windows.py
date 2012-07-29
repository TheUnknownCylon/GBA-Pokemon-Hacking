"""Sometimes, Windows behaves differently than linux. This file contains
methods to deal with this differences."""

import os
import sys

def fixworkingdir():
  '''When running a program in windows with drag-drop a file to the python
  file, windows starts in the workingdir %SYSTEM32%. Calling this method will
  correct the working directory, and sets it to the dir where the python file is
  located.'''
  os.chdir(os.path.dirname(sys.argv[0]))

