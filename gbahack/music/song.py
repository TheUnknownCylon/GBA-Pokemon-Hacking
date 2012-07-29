import json
import os
from array import array

import pokesuitelib.filesystem as fs
from gbamusicmanager.s import SReader

class Song():
  '''Representation of a song. A song is simply the voice group, and
  a set of tracks.'''
  def __init__(self, voicegroup, numblks, priority, reverb):
    self.voicegroup = voicegroup # pointer to a voicegroup
    self.numblks    = numblks
    self.priority   = priority
    self.reverb     = reverb
    self._tracks    = []
  
  def getTracks(self):
    '''Returns the list of tracks accompanied in the song.'''
    return self._tracks[:]

  def tracksCount(self):
    '''Returns the number of tracks in this song.'''
    return len(self._tracks)
      
  def addTrack(self, track):
    '''Add a new track to the song.'''
    self._tracks.append(bytearray(track))
    
    
  def dumpRaw(self, folder):
    '''Dumps the raw song information to a given folder.
    Each track will get its own file: trackid.bin
    Also other required metadata is stored in a songinfo.json file.'''
    songinfo = {
      'voicegroup': self.voicegroup,
      'numblks'   : self.numblks,
      'priority'  : self.priority,
      'reverb'    : self.reverb
    }
      
    fs.makedirs(folder)
    f = open("%s/info.json" % folder, 'w')
    f.write(json.dumps(songinfo))
    f.close()
      
    trackid = 0
    for trackid in range(0, len(self._tracks)):
      track = self._tracks[trackid]
      f = open("%s/%d.bin" %(folder, trackid), 'wb')
      f.write(array('B', track))
      f.close()
    
  @staticmethod
  def loadRaw(folder):
    '''Loads a song from a folder containing raw tracks and track information.'''
    trackinfo = json.loads(fs.getContent(folder+"/info.json"))
    
    song = Song(trackinfo['voicegroup'], trackinfo['numblks'], trackinfo['priority'], trackinfo['reverb'])
    
    trackindex = 0
    while os.path.isfile("%s/%d.bin"%(folder, trackindex)):
      song.addTrack(fs.getBinaryContent("%s/%d.bin"%(folder, trackindex)))
      trackindex+=1

    return song
  
  
  @staticmethod
  def loadFromS(file):
    from musicreader import RomMusicReader #Hmm, cyclic dependency :(
    import tempfile
    
    '''Loads a song from a s-file.'''
    #First convert the .s file to a ROM-file with all tracks
    s = SReader("/home/remco/downloads/Sappy/Mid2Agb/Dfleon.s")
    f = open("/tmp/.mytemp", 'w+b')
    s.getBytes().tofile(f)
    f.close()
    
    #Try to get the global pointer to the table
    keys = s.getGlobalKeys()
    if len(keys) != 1:
      raise Exception("Please specify exactly one key as global variable. This key should point to the song header.")
    pointertoheader = s.getDefined(keys[0])
    
    #Rely on the ROM-Song reader to get the track
    rom = RomMusicReader('/tmp/.mytemp', None)
    return rom.getSongByPointer(pointertoheader)
    
    
class SongRom(Song):
  '''Same class as Song, but also allows one to store pointers to tracks.'''
  def __init__(self, pointer, voicegroup, numblks, priority, reverb):
    Song.__init__(self, voicegroup, numblks, priority, reverb)
    self._pointer = pointer  #Pointer to song header
    self._pointers = []      #Pointer to tracks
  
  def addTrack(self, song, pointer=None):
    '''Add a track and its pointer to the ROM Song object.'''
    Song.addTrack(self, song)
    self._pointers.append(pointer)
  
  def getHeaderPointer(self):
    '''Returns the pointer to the header of the song in the ROM.'''
    return self._pointer
  
  def getPointer(self, trackindex):
    '''Returns the pointer to the start of a track in the ROM.'''
    return self._pointers[trackindex]
  