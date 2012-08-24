
from gbahack.gbabin.rawfile import RawFile

import json
import os

class NoMetaDataException(Exception): pass

class ROM(RawFile):
  def __init__(self, filename, metadata=None):
    RawFile.__init__(self, filename)
    self.filename = filename
    
    self.metadata = {}
    if metadata != None:
      self.metadata = metadata
    else:
      self.loadMetaData()
    
  def loadMetaData(self):
    self.metadata = {}
    
    #try to find a metadata rom definition
    metafile = None
    if os.path.isfile(self.filename+".metadata"):
      metafile = self.filename+".metadata"
    elif os.path.isfile(os.path.splitext(self.filename)[0]+".metadata"):
      metafile = os.path.splitext(self.filename)[0]+".metadata"
    else:
      NoMetaDataException("No metadata file was found for this ROM!")

    f = open(metafile, 'r')
    try: self.metadata = json.loads(f.read())
    except:
      print("Invalid metadata file. Should be in the JSON format!")
      raise NoMetaDataException()
    finally: f.close()
      


  def getName(self):
    if "name" in self.metadata:
      return metadata.name
    else:
      return "Unknown"
    