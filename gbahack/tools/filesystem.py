import os
import shutil

'''This file contains methods to interact with the filesystem.
Use this instead of os.* methods directly. It will help getting
the right debug messages.'''

def removedirs(resdir, force=True):
  if os.path.exists(resdir):
    print("> Removing directory %s" %resdir)
    if not force:
      os.removedirs(resdir)
    else:
      shutil.rmtree(resdir, ignore_errors=True)

def makedirs(resdir):
  #print("> Creating directory %s" %resdir )
  os.makedirs(resdir)
  
def getContent(filename):
  f = open(filename, 'r')
  c = f.read()
  f.close()
  return c
  
def getBinaryContent(filename):
  f = open(filename, 'rb')
  c = f.read()
  f.close()
  return c