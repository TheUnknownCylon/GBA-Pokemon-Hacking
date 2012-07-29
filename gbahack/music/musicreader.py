from array import array

from gbamusicmanager.song import SongRom

'''Reads song information from the game in raw format.
This information can be used to export songs. Other tools may be used to
generate .s, or .midi files from this.'''
class RomMusicReader():
  
  def __init__(self, rom, tablepointer):
    '''Initialize the tool.
    rom: File to read music from or write music to.
    managedir: Directory where read music is stored, and where music is put from into the file.
    tablepointer: Pointer where the music table can be found.
    '''
    self.rom = rom
    self.songtable = []
    self.tablepointer = tablepointer
    try: self.loadSongTable()
    except: raise Exception("Failed to parse the songtable.")
    
  def loadSongTable(self):
    '''The song table contains of the following hex data structures:
    AA BB CC DD EE FF GG HH, where AA BB CC DD is a pointer (I guess),
    and the use of EE FF GG HH is unknown to me (for now).
    
    The table ends where AA BB CC DD is equal to 00 00 00 00.
    Note that in this special case, we do not read EE FF GG HH, as
    this is not part of the table anymmore.
    '''
    
    p = self.tablepointer
    table = []
    while True:
      p, higher = self.rom.readPointer(p)
      if higher == 0: break            #End of song table
      p, lower = self.rom.readInt(p)   #TODO: Don't know what this is for...
      table.append((higher, lower))
    
    self.songtable = table
    print("> Table read")
    
  
  def hasSong(self, i):
    '''Returns True iff there is a song with the given index.'''
    return len(self.songtable) > i
  
  
  def getSong(self, i):
    return self.getSongByPointer(self.songtable[i][0])
    
    
  def getSongByPointer(self, p):
    headerpointer = p
    p, trackscount = self.rom.readByte(p)
    p, numblks = self.rom.readByte(p)
    p, priority = self.rom.readByte(p)
    p, reverb = self.rom.readByte(p)
    p, voicegroup  = self.rom.readPointer(p)
    
    song = SongRom(headerpointer, voicegroup, numblks, priority, reverb)
    
    for track in range(0, trackscount):
      p, tpointer = self.rom.readPointer(p)
      song.addTrack(self.getTrack(tpointer), tpointer)
    
    return song
  

  def getTrack(self, pointer):
    '''From a given track pointer, an array of all song-instructions
    is returned. Note that all pointers are relative to the song start
    pointer. (I.e. the jump pointers are relative.)'''
    p = pointer
    song = []
    
    while True:
      p, byte = self.rom.readByte(p)
      song.append(byte)
      
      if byte == 0xB1:
        break
      
      ## The following are jump instructions, and let the music jump to a new location
      elif byte == 0xB2 or byte ==0xB3:
        p, jumppointer = self.rom.readPointer(p)
        jumppointer -= pointer #store relative jump pointer
        
        for jbyte in array('B', ((jumppointer >> (i * 8)) & 0xFF for i in range(4))):
          song.append(jbyte)
        
      ## The following are instruction bytes which take one byte as next instruction
      #  Parse these bytes here, so they will not be used as special oparators.
      elif byte in (0xBB, 0xBC, 0XBD, 0xBE, 0xBF, 0xC0, 0xC1):
        p, byte = self.rom.readByte(p)
        song.append(byte)

    return song
    