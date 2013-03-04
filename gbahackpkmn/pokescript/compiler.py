
'''
Module that contains a Pokescript compiler,
compiling plain text code to an AST, and
AST to instruction bytes encoding.
'''

from gbahack.tools.numbers import toint

from gbahackpkmn.strings import PokeString
from gbahackpkmn.movements import Movement as PokeMovement
import gbahackpkmn.pokescript.ast as ast

from gbahackpkmn.pokescript.routine import Routine
from gbahackpkmn.pokescript.script import ScriptGroup
from gbahackpkmn.pokescript.langcommands import ParamType



###############################################_
### Exceptions


class NoRoutineException(Exception):
    '''An instruction is given, but no routine was opened yet.'''
    pass

class WrongCommandException(Exception):
    '''An instruction of the wrong type is given.'''
    pass


###############################################_
### The real stuff

class ScriptParser():
    '''
    Private class, do not use this outside this module!
    '''
    def __init__(self, langdef):
        self.langdef = langdef
        self._scriptgroup = ScriptGroup()
    
    def scriptgroup(self):
        '''Returns the scriptgroup with all registered resources.'''
        return self._scriptgroup
        
        
    def routineDef(self, name):
        '''Get a new routine, which will be registered as a known resource.'''
        r = Routine()
        self._scriptgroup.register(r, varname=name)
        return r
    
    def textDef(self, name):
        '''Get a new string, which will be registered as a known resource.'''
        r = PokeString()
        self._scriptgroup.register(r, varname=name)
        return r
        
    def movementDef(self, name):
        '''Get a new movement, which will be registered as a known resource.'''
        r = PokeMovement()
        self._scriptgroup.register(r, varname=name)
        return r
        
        
    def parselines(self, lines, resource):
        '''
        Parses a set of lines, returning a list resources.
        Note that the AST is not analyzed yet for errors!
        
        Returns the last working resource.
        '''
        for line in lines:
            resource = self.parseline(line, resource)
        return resource
    
    
    
    def parseline(self, line_raw, resource):
        line = line_raw
        
        #remove any comments, if any
        commentstart = line.find("'")
        if commentstart >= 0:
            line = line[:commentstart]
        
        line = line.lstrip()
        lineargs = self._line2args(line)
        
        if len(lineargs) == 0:
            return resource
        
        command = lineargs[0]
        args = lineargs[1:]
        
        if command == "#script":
            offset = args[0]  #TODO Validate
            return self.routineDef(offset)

        if command == "#text":
            offset = args[0]  #TODO: Validate
            return self.textDef(offset)
        
        if command == "#movement":
            offset = args[0]
            return self.movementDef(offset)
        
        if command[0] == "$":
            #$var = Hi I'm John! is sugar for #inline $var
            return self.parseline ("#inline "+line, resource)

        #Handle inline commands: #inline $Variable = Hi I'm John!
        if command == "#inline":   
            offset  = args[0]  #TODO: Validate
            #ctype   = args[1]  #TODO: Make use of it :)
            
            raise Exception("TODO, not supported yet") #TODO
            
            #All done, inline is over. Continue with normal param
            return resource
        
        #A set of raw commands is added to the stream
        if command == "#binary" or command == "#raw":            
            if not isinstance(resource, Routine):
                raise WrongCommandException()
                
            for byte in args:
                resource.ast().append(ast.ASTByte(toint(byte)))
            return resource
        
        #Parse movements
        if command[0] == ":":
            if not isinstance(resource, PokeMovement):
                raise WrongCommandException
            
            for byte in args:
                resource.append(toint(byte))
            return resource
        
        #Parse strings
        if command[0] == "=":
            if not isinstance(resource, PokeString):
                raise WrongCommandException()
            
            resource.append(line_raw[1:].lstrip())
            return resource
        
        
        # Still here? -> No pre-defined elements, check aliases and commands for
        #                possible command-compile 

        #Try to find an alias for this line, if it is there, take it.
        # Only if there is no matching alias, we look for a command to match
        for alias in self.langdef.aliases:
            if alias.matches(line):
                rawargs = self._prepargs(alias, alias.stripParams(line))
                resource.ast().append(ast.ASTCommand(alias, rawargs))
                return resource
            
        
        #Parse a command
        if command in self.langdef.commands:
            if not isinstance(resource, Routine):
                raise WrongCommandException()
            
            lcommand = self.langdef.commands[command]
            rawargs = self._prepargs(lcommand, args)

            resource.ast().append(ast.ASTCommand(lcommand, rawargs))
            return resource
        
        raise Exception("Could not parse line, no rules matched: %s"%line)
    
    
    def _prepargs(self, command, args):
        #Rewrite references to AST Reference nodes
        rawargs = []
        i_args = 0
        for i in range(0, len(command.params)):
            commandparam = command.getParam(i)
            #print(repr(commandparam))
            if commandparam.defaultvalue == None:
                #print(" -> consume! "+repr(args[i_args]))
                if ParamType.ispointer(commandparam.ptype):
                    rawargs.append(ast.ASTRef(args[i_args]))
                elif commandparam.definevaluestype != None:
                    defines = self.langdef.getDefines(commandparam.definevaluestype)
                    #Reversed defines lookup, not as elegant as I hoped it
                    key = args[i_args].upper()
                    val = None
                    try:
                        #If defines is a list:
                        try:
                            val = defines.index(key)
                        except:
                            val = next((dval for dval, dkey in defines.items() if dkey == key))
                        rawargs.append(ast.ASTDefinedValue(key, val))
                    except:
                        #There is no define for the value, parse it as is
                        # but then ofc. it should be an int.
                        try:
                            rawargs.append(toint(args[i_args]))
                        except:
                            raise Exception("%s is not defined, and could not be converted to an integer!"%args[i_args])
                else:
                    rawargs.append(toint(args[i_args]))
                i_args += 1
        return rawargs
        
    
    def _line2args(self, line):
        '''
        Normalizes the arguments. Returns a list of lowercased arguments.
        Note that this will not be sufficient for String parsing: multiple spaces
        are treated as single spaces.
        '''        
        line = line.strip()
        if not line:
            return []
              
        return line.lower().replace("\t", " ").strip().split()
    
    