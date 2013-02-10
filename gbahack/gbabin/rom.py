
from gbahack.gbabin.bytes import ByteArrayReader
from gbahack.resource import ResourceManager

import json
import os
from array import array

class NoMetaDataException(Exception):
    pass

class RawFile(ByteArrayReader):
    def __init__(self, file):
        self.file = file
        self.f = None
        self.bytes = []
        self._resetfile()
    
    
    def __getitem__(self, v):
        return self.f[v]
    
    
    def _resetfile(self):
        self.bytes = open(self.file, 'rb').read()  #read, adjust, in binary
    
    
    def path(self):
        '''Returns the path of the loaded file'''
        return self.file
  
    
    def trunc(self, offset, length, truncbyte=0xFF):
        '''Clears length bytes at a given offset in the ROM.
        Optional trunc byte can be set.'''
        c = array('B', [truncbyte] * length)
        self.writeArray(offset, c)
    
    
    def writeArray(self, offset, array):
        mf = open(self.file, 'r+b')
        mf.seek(offset)
        mf.write(array)
        mf.close()
        self._resetfile()    
  
  
    def write(self, offset, data):
        '''Writes a bblock object to the ROM'''
        self.writeArray(offset, data.toArray())
    
    
    def writeBlocks(self, bblockarray):
        '''Writes a dict of bblocks (accompanied by a offset as index) to the ROM.'''
        for offset in bblockarray:
            self.write(offset, bblockarray[offset])
    
    def size(self):
        return len(self.bytes)
  

class ROM(RawFile):
    def __init__(self, filename, metadata=None):
        RawFile.__init__(self, filename)
        self.filename = filename
    
        self.metadata = {}
        if metadata != None:
            self.metadata = metadata
        else:
            self.loadMetaData()
      
        self.resourcemanger = ResourceManager(self)
    
    
    def loadMetaData(self):
        self.metadata = {}
    
        #try to find a metadata rom definition
        metafile = None
        if os.path.isfile(self.filename+".metadata"):
            metafile = self.filename+".metadata"
        elif os.path.isfile(os.path.splitext(self.filename)[0]+".metadata"):
            metafile = os.path.splitext(self.filename)[0]+".metadata"
        else:
            raise NoMetaDataException("No metadata file was found for this ROM!")

        f = open(metafile, 'r')
        try:
            self.metadata = json.loads(f.read())
        except:
            print("Invalid metadata file. Should be in the JSON format!")
            raise NoMetaDataException()
        finally:
            f.close()
    
    
    def getRM(self):
        '''Returns the resource manager attatched to the ROM.'''
        return self.resourcemanger
    
    
    def getName(self):
        if "name" in self.metadata:
            return metadata.name
        else:
            return "Unknown"
