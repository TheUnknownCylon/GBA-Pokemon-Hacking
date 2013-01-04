from array import array
import struct

from gbahackpkmn.pokescript.lang import ParamType
from gbahackpkmn.strings import PokeString
from gbahackpkmn.movements import Movement as PokeMovement

class Decompiler():
  def __init__(self, langdef, rom):
    self.langdef = langdef
    self.rom = rom
    
  def decompile(self, scriptpointer):
    '''Decompiles a script and all its other subscript at a given pointer.
    A list of pointers and their scripts are returned.'''  
    return DecompileJob(self.langdef, self.rom, scriptpointer).routines  
  

class NotAMatchException(Exception): pass
class EndOfScript(Exception):
  def __init__(self, commandline):
    self.commandline = commandline
  
  
class DecompileTypes:
  POKESCRIPT = 0x00
  STRING     = 0x01
  MOVEMENT   = 0x02
    

    
class DecompileJob():
  def __init__(self, langdef, rom, scriptpointer):
    self.langdef = langdef
    self.rom = rom
    
    #Store all compiled scripts
    self.routines = {}
    
    #queue of scripts to decompile.
    self.pointerqueue = {scriptpointer: DecompileTypes.POKESCRIPT} 
    
    while len(self.pointerqueue) > 0:
      pointer = list(self.pointerqueue.keys())[0]
      ptype = self.pointerqueue.pop(pointer)
      
      #Do not decompile already decompiled routines
      if pointer in self.routines: continue

      if ptype == DecompileTypes.POKESCRIPT:
        routine = self.decompileRoutine(pointer)
      elif ptype == DecompileTypes.STRING:
        routine = self.decompileString(pointer)
      elif ptype == DecompileTypes.MOVEMENT:
        routine = self.decompileMovement(pointer)
      else: raise Exception("BUG! No such routine type.")

      self.routines[pointer] = routine

    
    
  def queue(self, pointer, ptype):
    '''Add a script pointer to the queue of scripts to be decompiled.'''
    self.pointerqueue[pointer] = ptype
 
 
  def decompileString(self, pointer):
    text = PokeString.read(self.rom, pointer).getText()
    return ["#ORG 0x%X"%pointer, "= %s"%text]

  
  def decompileMovement(self, pointer):
    print("Decompile movement %X\n"%pointer)
    movements = PokeMovement.read(self.rom, pointer).getMovements()
    
    instructions = ""
    for byte in movements:
      instructions += "0x%x"%byte +" "
      
    return ["#ORG 0x%X"%pointer, "; %s"%instructions]

    
  def decompileRoutine(self, pointer):
    '''Decompiles a script from the ROM at the given pointer.'''
    print("Decompile routine %X\n"%pointer)
    routine = ["#ORG 0x%X"%pointer]
    
    p = pointer
    while True:
      try:
        p, commandline = self.decompileCommand(p)
        print("  >> %s"% commandline)
        routine.append(commandline)
      except EndOfScript as e:
        routine.append(e.commandline)
        break
      except Exception as e:
        raise
      
    return routine
  
  
  def decompileCommand(self, pointer):
    '''Decompile a command at a given pointer.'''
    
    #Try to find a matching alias, if there is no matching
    # alias we try to find a mathcing command
    for command in self.langdef.aliases + list(self.langdef.commands.values()):
      p = pointer
      argbytes = array('B')
      try:
        for byte in command.bytesignature():
          p, v = self.rom.readByte(p)
          if byte != '' and byte != v: raise NotAMatchException()
          if byte == '': argbytes.append(v)
        
        print("Selected command to parse: "+' '.join(command.signature))
        #read the entire command bytes, and this all matches!
        try:
          commandstring = self.parsecommandargs(command, argbytes)
        except Exception as e:
          raise Exception("Failed to parse rewrite command and its args to a"
            + "correct line!\n Command signature: %s.\n Exception: %s."
            %(repr(' '.join(command.signature)), str(e)))
        
        if command.endofscript == True: raise EndOfScript(commandstring)
        else: return p, commandstring
        
      except NotAMatchException: pass  #try next command
      except EndOfScript as eos: raise eos

    p, thebyte = self.rom.readByte(pointer)
    print("Selected command: #raw 0x"+str(thebyte))
    return pointer+1, "#raw 0x"+str(thebyte)
   
   
  def parsecommandargs(self, command, argbytes):
    '''Rewrites the command to a String.
    The argbytes contains a BYTE-array of all values. These are read
    from it and appended to the command.'''
    
    commandsig = command.signature[:]
    
    p = 0
    argindex = 0
    for param in command.params:
      paramtype = param[0]
      paramdefault = param[1]
      
      # TODO TODO TODO TODO TODO
      #TODO: See if RawFile can be generalized and can accept bytestrings as well
      if paramdefault == None and paramtype != ParamType.eos:
        
        if paramtype == ParamType.byte:
          value = argbytes[p]
          p+=1
          
        elif paramtype == ParamType.word:
          value = struct.unpack("<H", argbytes[p:p+2])[0]
          p+=2
          
        elif ParamType.ispointer(paramtype):
          value = struct.unpack("<I", argbytes[p:p+4])[0] - 0x08000000
          if value < 0:
            raise Exception("Pointer expected!")
          if paramtype == ParamType.pointer_text:
            self.queue(value, DecompileTypes.STRING)  
          elif paramtype == ParamType.pointer_movement:
            self.queue(value, DecompileTypes.MOVEMENT)
          else:
            self.queue(value, DecompileTypes.POKESCRIPT)
          p += 4
            
        elif ParamType == ParamType.int:
          value = struct.unpack("<I", argbytes[p:p+4])[0]
          p += 4
   
        #replace $argindex in command thingy with 0xvalue
        # note that in the syntax def, these values are counted from $1, not $0!
        commandsig[commandsig.index("$%d"%(argindex+1))] = "0x%X"%value
        argindex += 1
      
    return ' '.join(commandsig)
   