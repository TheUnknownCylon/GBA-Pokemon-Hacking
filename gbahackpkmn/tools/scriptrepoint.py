
'''The method repoint will repoint script pointers after burning scripts to the ROMs.
The pointers to be burned have to be specified in a special configfile.

The config file syntax is very straighforward and defined below.
  'comments can be given after '
  $pointername bank map type=[person|sign|script] number:
Example:
  $helloworld 3 0 person 1   #Set script of person 1 on map 0 of bank 3 to the new pointer


'''
from gbahackpkmn.pokemap import PokeMapManager


def isint(i):
  try: int(i)
  except: return False
  return True

def repoint(rom, mappointer, newpointers, lookupfile):
  gamemap = PokeMapManager(rom, mappointer)
  
  for line in open(lookupfile, encoding="utf-8"):
    line = line.split("\'")[0].strip()
    if len(line) == 0: continue
    normalized = " ".join(line.replace("\t", " ").split())
    args = normalized.split(" ")
    
    #check args
    if len(args) != 5:
      raise Exception("Malformed line, needs 5 parameters.\nLine: %s"%line)
       
    scriptname = args[0]
    mapbank    = args[1]
    mapid      = args[2]
    scripttype = args[3]
    scriptid    = args[4]
    if not scriptname[0] == "$": raise Exception("Not a valid pointer name (add a $ ??): %s"%scriptname)
    if not isint(mapbank): raise Exception("Bank should be an integer, got %s."%mapbank)
    if not isint(mapid) : raise Exception("Map should be an integer, got %s."%mapid)
    if not (scripttype == "script" or scripttype =="person" or scripttype=="sign"):
      raise Exception("Type should be script, people or sign. Got: %s."%scripttype)
    if not isint(scriptid): raise Exception("Number should be an integer, got %s"%scriptid)
    
    #if this script is updateable
    if scriptname[1:] in newpointers:
      events = gamemap.getMap(int(mapbank), int(mapid)).events 

      script = events.get(scripttype, int(scriptid))
      script.scriptpointer = newpointers[scriptname[1:]]
      events.write(scripttype, int(scriptid), script)
        
      print("Updated pointer to script of %s on map %s of bank %s."%(scripttype, mapid, mapbank))
      
    