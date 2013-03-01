import struct
from array import array
from gbahackpkmn.pokescript.lang import toint


class Routine():
    def __init__(self):
        self._codes = array('B')
        
    def addByte(self, byte):
        self._codes.append(byte)
        
    def addBytes(self, otherarray):
        self._codes.extend(otherarray)
    
    def overwrite(self, index, byte):
        self._codes[index] = byte
    
    def getBytes(self):
        return self._codes
    
    def length(self):
        return len(self._codes)
    

class RoutineText(Routine):
    def getBytes(self):
        return self._codes + array('B', [0xff])
    
    def length(self):
        return super().length() + 1


class PokeScript():
    def __init__(self, langdef, filename):
        self.langdef = langdef #Store the language which we are parsing
        
        self.pointerdefs = {}  #index:name, value:routine
        self.pointerrefs = []  #(routine, ref, index)
        
        self.routine = None    #holds the current parsing routine
        
        try:
            self.parsefile(filename) #Parse the input
            self.validatePointers()  #Make sure that all pointerrefs are correct
        except Exception:
            raise
            #print(" Parsing failed: "+str(e))
        
    
    def routineDef(self, name, bank=0):
        '''Get a new routine, which will be registered as a known routine.'''
        r = Routine()
        self.pointerdefs[name.lower()] = r
        return r
    
    def textDef(self, name, bank=0):
        '''Get a new routine, which will be registered as a known routine.'''
        r = RoutineText()
        self.pointerdefs[name.lower()] = r
        return r
        
        
    def validatePointers(self):
        '''This method will validate all pointers, are all pointerrefs present as pointerdefs?'''
        for pointer in self.pointerrefs:
            if not pointer[1] in self.pointerdefs:
                raise Exception("Pointer %s is not defined!"%pointer[1])
    

    def updatepointers(self, pointertable):
        for pointer in self.pointerrefs:     #For each known ref, check if there is a pointer to update
            if pointer[1] in pointertable:     #If there is an update
                self.updatepointer(pointer[0], pointer[2], pointertable[pointer[1]])
    
    
    def updatepointer(self, routine, offset, value):
        value += 0x08000000             #GBA pointer offset
        pointerbytes = array('B', struct.pack("<I", value))
        routine.overwrite(offset,   pointerbytes[0])
        routine.overwrite(offset+1, pointerbytes[1])
        routine.overwrite(offset+2, pointerbytes[2])
        routine.overwrite(offset+3, pointerbytes[3])
        

    def parsefile(self, filename):
        self.parselines(open(filename), None)
    
    
    def parselines(self, lines, routine):
        for line in lines:
            try: routine = self.parseline(line, routine)
            except Exception: raise
            #raise Exception("Error in line:\n %s %s\n "%(line, str(e)))
        return routine
        
    def parseline(self, line, routine):
        '''Parses a line of the script. THe method returns the routine object
        parsing is doing (from) now (on).'''
        print(">> %s"%line)
        linenorm = self.normalizeline(line)
        if len(linenorm) == 0: return routine

        command = linenorm[0]
        args = linenorm[1:]
        
        if command == "#script":
            offset = args[0]
            if offset[0] == "$":
                return self.routineDef(offset[1:])
            else:
                raise Exception("Currently there is only support for routine definitions starting with $: e.g.: #ORG $NAME")


        if command == "#text":
            offset = args[0]
            if offset[0] == "$":
                return self.textDef(offset[1:])
            else:
                raise Exception("Currently there is only support for routine definitions starting with $: e.g.: #ORG $NAME")

                

                
        if command[0] == "$":
            #$var 1 = Hi I'm John! is sugar for #inline $var 1
            return self.parseline ("#inline "+line, routine)
                
                
        if command == "#inline":   #inline $Variable 1 = Hi I'm John!
            offset = args[0]
            #bank     = args[1]
            ctype     = args[2]
            
            if offset[0] == "#": raise Exception("Incorrect offset: only $vardef is supported.")
            if offset[0] != "$": raise Exception("Offset expected.")
            if "=" in offset or ";" in offset: raise Exception("Please do not use = or ; in the offset name.")
            
            #TODO: Okay, this can give bugs if using = or ; in one of the arguments
            innerroutine = self.routineDef(offset[1:])
            if ctype == "=": #Rewrite all after = to a String
                string = line.split("=", 1)[1].strip()
                innerroutine.addBytes(self.langdef.encodeText(string))
            elif ctype == ";": #Rewrite rest as a normal command
                string = line.split(";", 1)[1]
                self.parseline(string, innerroutine)
            else:
                raise Exception("= or ; excpected, got %s."%ctype)
            
            #All done, inline is over. Continue with normal param
            return routine
        
        
        if command == "#binary" or command == "#raw":
            if routine == None: raise Exception("#binary or #raw should be part of a routine.")
            for byte in args:
                routine.addByte(toint(byte))
            return routine
        
        if command[0] == "=":
            string = line.split("=", 1)[1].strip()
            routine.addBytes(self.langdef.encodeText(string))
            return routine
            
        
        #Try to find an alias for this line, if it is there, take it.
        # Only if there is no matching alias, we look for a command to match
        for alias in self.langdef.aliases:
            if alias.matches(line):
                lines = alias.desugar(line)
                return self.parselines(lines, routine)
            
        
        #Parse a command
        if command in self.langdef.commands:
            if routine == None:
                raise Exception("Parsing command before routine declaration!")
            
            self.handleCommand(command, args, routine)
            return routine
        
        raise Exception("Could not parse line, no rules matched: %s"%line)
        

        
    def handleCommand(self, command, args, routine):
        commands = self.langdef.commands
        scriptcommand = commands[command]
        
        commandbytes, pointers = scriptcommand.compile(routine.length(), *args)
        for pointer in pointers:
            self.pointerrefs.append((routine, pointer[0], pointer[1]))
        routine.addBytes(commandbytes)
        
        