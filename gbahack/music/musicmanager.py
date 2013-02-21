from gbahack.music import RomMusicReader
from gbahack.music import RomMusicWriter
import gbahack.tools.filesystem as fs

# The following documentation document the GBA-music code. 
# Note that is information I gathered myself from inspecting a ROM,
# and reading information on the web. It may, or may not be, usefull for you
# to read. It does not describe the musicmanager application in an explicit way.
#
# The GBA Rom Datastructure:
#  There is a table which contains pointers to all songs
#    (pointer, int:???)
#
#  Each song contains of a header, followed by the songs directly
#  The header:
#     1. short:   number of tracks
#     2. short:   unknown
#     3: pointer: voicegroup
#     4 -for each track in the song-: pointer: start of track
#
#  Usually (by the GBA compiler??) the header is directly followed by 
#  the tracks (check the track pointers). Each track is a list of track-commands.
#  
#  Please refer to the readme for the byte code instructions.
#

'''Usage example, dump all tracks of firered into folders:
   x = RomMusic("firered.GBA", "/tmp/rommusic/", 0x4A32CC)
   x.dumpFromRom()
'''
class RomMusic():
    def __init__(self, rom, tablepointer):   
        self.rom = rom
        self.tablepointer = tablepointer

    def dumpAll(self, romdir):
        '''Get all songs from the ROM and store them in binary format in the specified dir.'''
        reader = RomMusicReader(self.rom, self.tablepointer)
        fs.removedirs(romdir)
        fs.makedirs(romdir)
    
        for songindex in range(0, len(reader.songtable)):
            songdir = "%s/%d" % (romdir, songindex)
            song = reader.getSong(songindex)
            song.dumpRaw(songdir)
      
    def writeSong(self, index, song):
        '''Write a single song to the ROM.'''
        writer = RomMusicWriter(self.rom, self.tablepointer)
        writer.writeSong(index, song)

  
    def writeSongs(self, songdict):
        '''Get a dict of songs, the dict index represents the song id.
        First all selected songs are removed from the ROM, and are written back.
        It may remove some free space fragmentation.'''
        writer = RomMusicWriter(self.rom, self.tablepointer)
    
        # check that we are going to write valid songs (pointers)
        for index in songdict:
            try: int(index)
            except: raise Exception("All song indices should be integers, got something else: " + repr(index))
            writer.assertSong(index)
    
        # Free all possible space
        for index in songdict:
            writer.truncSong(index)
    
        # Finally write!
        writer.writeSongs(songdict)

