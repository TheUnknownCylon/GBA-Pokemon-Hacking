from gbahackpkmn.pokescript.ast import *
from gbahackpkmn.strings import PokeString
from gbahackpkmn.movements import Movement as PokeMovement
from gbahackpkmn.pokescript.routine import Routine
from gbahackpkmn.pokescript.langcommands import ParamType

import struct


def _ptype_to_decompiletype(paramtype):
    '''ParamType to DecompileType conversion'''    
    if paramtype == ParamType.pointer_text:
        return DecompileTypes.STRING
    elif paramtype == ParamType.pointer_movement:
        return DecompileTypes.MOVEMENT
    else: #TODO: is this true? can it be distuingished?
        return DecompileTypes.POKESCRIPT
    

class DecompileTypes:
    POKESCRIPT = 0x00
    STRING     = 0x01
    MOVEMENT   = 0x02


class Decompiler():
    '''
    Decompiler, decompiles script and returns
    '''    
    def __init__(self, rom):
        self.rom = rom             
        
    def decompile(self, pointer, decompiletype):
        
        if decompiletype == DecompileTypes.POKESCRIPT:
            routine = self.decompileRoutine(pointer)
        elif decompiletype == DecompileTypes.STRING:
            routine = self.decompileString(pointer)
        elif decompiletype == DecompileTypes.MOVEMENT:
            routine = self.decompileMovement(pointer)
        else:
            raise Exception("BUG! No such routine type: %s."%repr(decompiletype))

        return routine

    def decompileString(self, pointer):
        '''Decompiles a String at a given pointer.'''
        return PokeString.read(self.rom, pointer)

    def decompileMovement(self, pointer):
        '''Decompiles a movement at a given pointer.'''
        return PokeMovement.read(self.rom, pointer)
    
    def decompileRoutine(self, pointer):
        '''Decompiles a routine at a given pointer.'''
        routine = Routine.read(self.rom, pointer)
        return routine    
    
    
class NotAMatchException(Exception):
    '''Internally used exception, in case a command signature does not match.'''
    pass


class CommandDecompiler():
    def __init__(self, langdef):
        self.langdef = langdef
    
    
    def decompileCommand(self, rom, pointer):
        '''
        Decompile a command at a given pointer.
        Returns 3 values: new pointer, ASTNode, reference-pointers.
        '''
        print("DECOMPILE 0x%X"%pointer)
        #Try to find a matching alias, if there is no matching
        # alias we try to find a mathcing command
        for command in self.langdef.aliases + list(self.langdef.commands.values()):
            p = pointer
            argbytes = array('B')
            try:
                for byte in command.bytesignature():
                    p, v = rom.readByte(p)
                    if byte != '' and byte != v:
                        raise NotAMatchException()
                    if byte == '':
                        argbytes.append(v)
        
                print("\nSelected command to parse: "+' '.join(command.signature))
                #read the entire command bytes, and this all matches!
                try:
                    #print(argbytes)
                    astnode, refs = self.parsecommandargs(command, argbytes)
                except Exception as e:
                    raise Exception("Failed to parse rewrite command and its args to a"
                        + "correct line!\n Command signature: %s.\n Exception: %s."
                        %(repr(' '.join(command.signature)), str(e)))
        
                return p, astnode, refs
            
            except NotAMatchException:
                pass  #try next command

        p, thebyte = rom.readByte(pointer)
        print("Selected command: #raw 0x"+str(thebyte))
        return pointer+1, ASTByte(thebyte), {} #no refs
        

    def parsecommandargs(self, command, argbytes):
        '''
        Rewrites the command to a AST Node with proper arguments set.
        
        The argbytes contains a BYTE-array of all values. These are read
        from it and appended to the command.
        '''
        print(">>> ", argbytes)
        args = []
        
        p = 0
        for param in command.params:
            paramtype = param[0]
            paramdefault = param[1]

            if paramdefault == None and paramtype != ParamType.eos:
                if paramtype == ParamType.byte:
                    value = argbytes[p]
                    p+=1
          
                elif paramtype == ParamType.word:
                    value = struct.unpack("<H", argbytes[p:p+2])[0]
                    p+=2
          
                elif ParamType.ispointer(paramtype):
                    pointer = struct.unpack("<I", argbytes[p:p+4])[0] - 0x08000000
                    value = ASTPointerRef(pointer, _ptype_to_decompiletype(paramtype))  #TODO paramtype,
                    p += 4
            
                elif paramtype == ParamType.int:
                    value = struct.unpack("<I", argbytes[p:p+4])[0]
                    p += 4
                    
                else:
                    print("Unknown ParamType: "+repr(paramtype))
   
                args.append(value)
      
        return ASTCommand(command, args), {} #TODO: Remove last arg
