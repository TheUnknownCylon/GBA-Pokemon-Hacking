
from gbahack.gbabin import BBlock
from gbahack.music.musicreader import RomMusicReader

class RomMusicWriter():
  
    def __init__(self, rom, tablepointer):
        self.rom = rom
        self.tablepointer = tablepointer
        self.reader = None
    
        #We are probably going to modify the ROM,
        # Load a RomMusicReader to get current music information from ROM
        self._resetReader()
    
    
    def _resetReader(self):
        self.reader = RomMusicReader(self.rom.path(), self.tablepointer)
    

    def writeSong(self, index, song):
        '''Writes a song to the ROM, if there is already a song
        at the given index, this song will be overwritten.'''
        rom = self.rom
    
        voicegroup = song.voicegroup
        tracks = song.getTracks()
    
        print("> Writing song %d" %index)
    
        #Step 1, check wheter there is a song to overwrite
        self.assertSong(index)
      
        #Step 2, free space: song header and all song tracks
        self.truncSong(index)
        print(" > Space freed")
    
        #Step 3, find space
        # TODO For now this tool stores an entire song at one location
        #      this could be separated in a later state of this software development.
        headerlength = 2+2+4 #short trackscount + short unknown + pointer voicegroup
        trackslength = 0
        for track in tracks:
            headerlength += 4          #pointer to track
            trackslength += len(track) #one byte for each track instruction
    
        newchunksize = headerlength+trackslength
        newpointer = rom.findSpace(0x6b5640, newchunksize)
        print (" > Storing at pointer %X"%newpointer)
        
        #Step 4, write song and tracks
    
        #4.1 Prepare all tracks and their pointers
        romtracks = {}
        tp = newpointer + headerlength
        for track in tracks:
            track = self.fixTrackPointer(tp, track)

            romtracks[tp] = BBlock.fromBytes(track)
            tp += len(track)
            #TODO: Add trailing 000 00 or 0 (so song end is aligned at a group of 4 bytes)

        #4.2 Generate the header
        header = BBlock()
        header.addByte(len(tracks))   # Number of tracks
        header.addByte(song.numblks)
        header.addByte(song.priority)
        header.addByte(song.reverb)
        header.addPointer(voicegroup)  # Used voicegroup for track
        for trackpointer in romtracks:
            header.addPointer(trackpointer)
    
        #4.3 Write header + tracks to rom
        rom.write(newpointer, header)
        rom.writeBlocks(romtracks)
    
    
        #Step 5, update table
        # -- todo: set newpointer in table as pointer to track index
        self.updateSongTable(index, newpointer)
    
  
    def updateSongTable(self, trackid, pointer):
        '''Rewrites a value in the songtable, so it plays the song at the given pointer.'''
        p = self.tablepointer + 8*trackid
        
        data = BBlock()
        data.addPointer(pointer)
        data.addInt(0x00)
        self.rom.write(p, data)

      
    def fixTrackPointer(self, startpointer, track):
        '''Takes a track, and prepares pointers for a ROM insertion'''
        i = 0
        while i < len(track):
            byte = track[i]
            i+=1
      
            if byte == 0xb2 or byte == 0xb3:
                #A pointer follows, fix the pointer
                pr = track[i:i+4]        
                p = (pr[3]<<24) + (pr[2]<<16) + (pr[1]<<8) + pr[0]
                p += startpointer + 0x08000000
        
                track[i+3] = (p & 0xFF000000) >> 24
                track[i+2] = (p & 0x00FF0000) >> 16
                track[i+1] = (p & 0x0000FF00) >> 8
                track[i  ] =  p & 0x000000FF 
      
                i+=4

        return track

    
    def truncSong(self, index):
        '''Removes a song from a ROM, and replaces it with 0xFF values.
        Also update the Song-table, replace with a pointer to song 0, which usually
        is silence.'''
        self.assertSong(index)
    
        romsong = self.reader.getSong(index)
        tracks = romsong.getTracks()
        headerpointer = romsong.getHeaderPointer()
    
        self.rom.trunc(headerpointer, 8+4*len(tracks)) #4 bytes + voicegroup pointer + pointer for each track
    
        #Header removed, no tracks to trunc
        if len(tracks) == 0:
            return
    
        for trackid in range(0, len(tracks)):
            trackpointer = romsong.getPointer(trackid)
            self.rom.trunc(trackpointer, len(tracks[trackid]))
      
        #If there are trailing 00 after the current song, remove them as well
        # Only remove until the a block of 4 bytes has ended
        p = trackpointer + len(tracks[trackid])
        while p % 4 > 0:
            p, v = self.rom.readByte(p)
            if v == 0x00:
                self.rom.trunc(p-1, 1)
            else:
                break

      
    def assertSong(self, index):
        '''Assertion to check whether the index is really a song in the table.'''
        if not self.reader.hasSong(index) == True:
            raise Exception("> E: Song %d not in table!" % index)
        
