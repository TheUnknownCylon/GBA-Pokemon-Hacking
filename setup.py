#!/usr/bin/env python

from distutils.core import setup

# Work around mbcs bug in distutils.
# This is done in order to compile a windows installer.
# http://bugs.python.org/issue10945
import codecs
try: codecs.lookup('mbcs')
except LookupError:
  ascii = codecs.lookup('ascii')
  func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
  codecs.register(func)

  
setup(name='GBAMusicManager',
      version='0.9',
      description='GBA Music Manager',
      author='Remco van der Zon',
      author_email='https://github.com/TheUnknownCylon/GBAMusicManager',
      url='https://github.com/TheUnknownCylon/GBAMusicManager',
      packages=[
        "gbahack", "gbahack.gbabin", "gbahack.music", "gbahack.tools",
        "gbahackpkmn", "gbahackpkmn.pokemap", "gbahackpkmn.pokescript",
        "gbahackpkmn.tools"
        ],
        
      package_data={"gbahackpkmn.pokescript":["langdef/*.psh"]}
  ) 
