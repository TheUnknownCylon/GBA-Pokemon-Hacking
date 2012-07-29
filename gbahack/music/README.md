GBA Music Manager
=================

Introduction
------------
GBA Music Manager is a ROM hack tool for all kind of Gameboy Advance games. The
tool is capable of reading music from, and writing to, a compiled GBA ROM. The 
tool is written in Python, so it will run on Linux as well as on Mac and Windows.

Features
--------
* OS Independent (compatible with python 2.7 and 3.x)
* Dumping all songs from a GBA ROM at once
* Inserting songs from raw format
* Inserting songs from a .s file 
* Edit music properties, such as voice groups, reverb and priority.
* Takes care of the song header: no manual hex editting required.
* Rewrites pointers in the song table: no manual hex editting required!

Limitations
-----------
* No .s, or no .midi output
* Only reads tracks which are of 1 piece in ROM (jumping to other parts of the ROM is not possible yet). Note that is not really a limitation, since all GBA ROMs have this.
* Not yet, but will be implemented soon: adding new tracks, instead of overwriting only
  
*If you wish, you can implement support for this, and merge it into this project
with a pull request.*


Usage
=====
In this section it is described how to use the tool. Note that this tool does
not come with a graphical user interface. In this documentation it will be
described how to write (automated) scripts which will do all tasks for you.

Dumping all tracks
------------------
In order to dump tracks from a ROM, a pointer to the music table should be known.
Fortunetaly a similar tool like this ([Sappy][3]) comes with a small list of
pointers. These pointers are included in this tool under songtables.txt.

Now create a simple Python application (for those who don't know Python, just
open a text editor such as notepad, and call your file "ripper.py"). Insert the
following code:

    from gbamusicmanager import RomMusic
    
    #Assume we have a Firered rom in the same folder as this script
    # the second argument is the table pointer of firered.
    firered = RomMusic("firered.gba", 0x4A32CC)
    
    #Now dump all the songs to the folder songs, all content of the folder is
    # overwitten!
    firered.dumpAll("songs")
    
Run this application in a terminal (Windows users: start cmd), cd to the folder
where you have stored your Python script, and run "python ripper.py". If all goes
without problems, you will have all the music ripped in the sub folder "songs".

### The dump output
In the output folder you will find multiple sub-folders. Each folder has a number
which represents the track number in the ROM. In each folder several .bin files
are present: each file represents a track of the song. You can open and edit these 
tracks with any HEX editor. The content format of these .bin files is described
later on in this readme.

Along with the tracks, there is a file "info.json". This file can be opened with
any text editor, such as notepad. It contains the track properties in JSON
format. The properties in this file are: voicegroup, numblks, priority and reverb.


Replace a song
--------------
For replacing a song, the output of a dump can be used. The following script
demonstrates how to take a song from Pokemon Ruby, and put it into FireRed.
Note that the voicegroup is changed in the Python code. This can also be done
by overwriting the voicegroup in .json configuration file.

    from gbamusicmanager import RomMusic, Song
    
    #Dump all tracks from Ruby
    ruby = RomMusic("ruby.gba", 0x45548C)
    ruby.dumpAll("songs_ruby")

    #Create a song-object with a just dumped track
    rubysong = Song.loadRaw("songs_ruby/405")
    #Note that we need to fix the voicegroup, otherwise no music will be heared
    rubysong.voicegroup = 0x48B474
    
    #Now lets write it into FireRed, we overwrite Pallet Town (300)
    firered = RomMusic("firered.gba", 0x4A32CC)
    firered.writeSong(300, rubysong)
    
Now start the rom, and play until you can control your character; the music you
hear is music from the Ruby game ported to firered.
    
Inserting a MIDI, inserting a ".s" file
---------------------------------------
It is possible to insert a MIDI file to a GBA ROM. This requires some human
interaction. A commonly used music editor is [Anvil Studio][1], but other
applications can be used as well. When you have a MIDI file, the MIDI can be
converted to a .s file. The latter can then be imported using the GBA Music
Manager. In order to convert the MIDI, use the tool [MID2AGB][2] (Windows only)
by dropping a ".midi" file into it. It will output the ".s" file.

Inserting a ".s" file into the ROM goes the same as inserting a "raw" song.
Just take the previous example, the song could now be loaded from a .s file:
    mysong = Song.loadFromS("mysong.s")


Hint
----
Although this is not GBA Music Manager specific, it is a good habit to work with
a copy of your ROM, in case something goes wrong. In Python a file can easily be
copied with the following commands:

    import shutil
    shutil.copyfile("firered.gba", "firered.backup.gba")
    

The Song format
===============
A lot of information can be found about the actual song format which the GBA
uses. When using this tool, the two most important things to keep in minde are
voicegroups and the binary format.

Voicegroups
-----------
According to [a post on PokeCommunity][4], the DS plays only a certain set of 
instruments. Not all these instruments can be played at the same time. A 
voicegroup is a set of instruments that can be used at the same time, and this
can be set on a per-song basis. Please read this post carefully if you are
writing your own songs, or moving songs from one ROM to another.

Another definition, along with all voice groups in Firered can be found [here][5], and for Ruby [here][6].

Binary format
-------------
The application output is a song in binary output. The GBA parsers this song by
reading instructions byte by byte. In the following table the instructions are
explained in little detail:

    B1: ends song as far as I can tell, a song is always ended with B1, also when looping.
    B2 <pointer>: loops song
    B3 <pointer>: Jump to other part of song
    B4: Return from other part of song
    BB <byte>: set tempo (offset?)
    BC <byte>: set pitch (offset)
    BD <byte>: set instrument
    BE <byte>: set volume
    BF <byte>: set spanning
    C0-CE : 
    CF-FF : Play a note.

Some pointers
=============

    Romcode	Songtable Game Name
    KWJ6	0x003ED0  Kawa's Jukebox 2006
    BDTE	0x2C6084  River City Ransom
    AW2P	0x2C5638  Advance Wars 2
    A7KE	0x60B460  Kirby: Nightmare in Dream Land
    AXVE	0x45548C  Pokémon Ruby
    AXPE	0x4554E8  Pokémon Sapphire
    BPRE	0x4A32CC  Pokémon Fire Red
    BPGE	0x4A2BA8  Pokémon Leaf Green
    B3SE	0x0EB420  Sonic Advance 3
    AMKE	0x102498  Mario Kart Super Circuit [U]	
    ASBJ	0x04132C  Phoenix Wright
    
__source of these pointers: [Sappy][3]__
    
[1]:http://www.anvilstudio.com/
[2]:http://feomni.57o9.org/FE%20Omni/Music/Mid2Agb/
[3]:http://filetrip.net/gba-downloads/tools-utilities/download-sappy-2006-mod-16-f29862.html
[4]:http://www.pokecommunity.com/showthread.php?t=139156
[5]:http://www.pokecommunity.com/showthread.php?t=148811
[6]:http://www.pokecommunity.com/showthread.php?t=158512
[7]:https://github.com/TheUnknownCylon/GBAMusicManager/zipball/master
[8]:https://github.com/TheUnknownCylon/GBAMusicManager/downloads
[9]:http://www.python.org/getit/
[10]:https://github.com/TheUnknownCylon/GBAMusicManager/pulls
[11]:https://github.com/TheUnknownCylon/GBAMusicManager/issues