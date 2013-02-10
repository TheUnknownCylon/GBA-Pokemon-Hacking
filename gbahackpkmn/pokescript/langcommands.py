import struct
from array import array
from gbahack.tools.numbers import toint

class Param:
    '''
    Simple parameter-class, holds all info for a parameter,
    such as type, description, default type and defined values class.
    '''
    def __init__(self, ptype=None, defaultvalue=None, description=None, definevaluestype=None):
        self.ptype = ptype
        self.description = description
        self.defaultvalue = defaultvalue
        self.definevaluestype = definevaluestype
        

class ParamType:
    '''Represents all allowed parameter types'''
    byte    = 0x00
    word    = 0x01
    int     = 0x02
    pointer = 0x03
    eos     = 0x04 #end of script
    command = 0x07 #name of command to call
    pointer_text = 0x08
    pointer_movement = 0x09
    
    @staticmethod
    def ispointer(type):
        if type == ParamType.pointer: return True
        if type == ParamType.pointer_text: return True
        if type == ParamType.pointer_movement: return True
        return False
    
    @classmethod
    def rewrite(cls, type, value):
        try:
            return cls.rewritehelper(type, value)
        except:
            raise Exception("Could not rewrite value %s of type %X."%(repr(value), type))
    
    @staticmethod
    def rewritehelper(type, value):
        if type == ParamType.byte:
            return struct.pack("<B", value)
        elif type == ParamType.word:
            return struct.pack("<H", value)
        elif ParamType.ispointer(type) or type == ParamType.int:
            return struct.pack("<I", value)
        raise Exception("Could not rewrite value: got wrong argument type: %x."%type)


class CodeCommand():
    '''
    Abstract representing commands (statements) that can be used in the PokeScript
    language. Each command can have one or multiple parameters, that needs to
    be set in the script. Also a description for the command and their arguments
    can be retrieved via get-methods.    
    '''
    
    def __init__(self):
        self.params = []
        self.neededparams = 0
        self.endofscript = False
        self.description = ""
    
    
    def setDescription(self, description):
        self.description = description
    
    
    def getDescription(self):
        '''Returns a description for the given command.'''
        return self.description
    
        
    def addParam(self, paramtype, defaultvalue=None, definevaluestype=None, description=None):
        '''
        Adds a parameter to the command. Note that values without a default
        are the values that should be set by the user.
        '''
        
        #Pokescript does some additional footers which are not required!
        if paramtype == ParamType.eos:
            self.endofscript = True
            return
            
        self.params.append(Param(paramtype, defaultvalue, description, definevaluestype))
        
        if defaultvalue == None:
            self.neededparams+=1
            defaultvalue = None
    

    def getParams(self):
        '''Returns tuple of parameters required for this command.
        Note that Parameters with default one are the only ones that should
        be actually provided in a statement (the default ones are used by the
        compiler for aliasses).'''
        return self.params
    

    def getParam(self, i):
        '''Returns the i-th parameter as (PType, default value) tuple.
        Note: these are params used by the compiler, and not user input params.'''
        return self.params[i]
    
    
    def checkParamscount(self, argscount):
        if argscount != self.neededparams:
            raise Exception("Wrong number of arguments used: got %d, expected %d."%(argscount, self.neededparams))

    
    def compile(self, *args):
        '''Compiles the command according to a list of arguments.'''
        raise NotImplementedError()
    
    
    def bytesignature(self):
        '''
        Returns the byte signature for the given CodeCommand, argument slots
        are left empty.
        '''
        raise NotImplementedError()

            
class Alias(CodeCommand):
    '''An alias is a shortcut definition for several commands and arguments.
    An alias can not be compiled, but can be desugared. This means that
    the alias is rewritten to the commands it actually represents. These lines
    can then be parsed as normal commands.'''
    def __init__(self, string, commands):
        CodeCommand.__init__(self)
        self.signature = string.lower().split()
        self.commands = commands #pointer to list of all commands, needed for desugaring
        self._bytesig = None
        
        
    def matches(self, line):
        try:
            self.stripParams(line)
        except:
            return False
        return True
    
    def userargsorder(self):
        '''Returns the order of which user args are required,
        it is possible to first get $2, and next $1.'''
        ordered = []
        for sigarg in self.signature:
            if sigarg[0] == "$":
                ordered.append(toint(sigarg[1:]))
        return ordered
        
    def stripParams(self, matchstr):
        params = []
        match = matchstr.lower().split()
        if len(match) != len(self.signature): raise Exception("Not a match!")
        
        for i in range(0, len(self.signature)):
            if self.signature[i][0] == "$":
                params.append(match[i])
            elif self.signature[i] != match[i]: raise Exception("Not a match!")

        #Shuffle the params according to their occurrence in the signature
        sorted_params = []
        for index in self.userargsorder():
            sorted_params.append(params[index - 1])
        
        return sorted_params
    
    
    def bytesignature(self):
        if self._bytesig == None:
            self._bytesig = self._generate_signature()
        return self._bytesig
    
        
    def _generate_signature(self):
        sig = []
        skip = 0
        for paramindex in range(0, len(self.params)):
            param = self.params[paramindex]
            
            #We have to skip a param, because it was consumed with another called command
            if skip > 0:
                skip -= 1
                continue
            
            paramtype    = param.ptype
            paramdefault = param.defaultvalue
            
            if paramdefault == None:
                valuestoappend = [''] * len(ParamType.rewrite(paramtype, 0))
            elif paramtype == ParamType.command:
                currentparamindex = paramindex + 1
                command = self.commands[paramdefault.lower()]
                
                commandefaultargs = []
                for parami in range(0, command.neededparams):
                    parami_default = self.params[currentparamindex + parami].defaultvalue
                    if parami_default == None: commandefaultargs.append(None)
                    else: commandefaultargs.append(parami_default)
                
                valuestoappend = command.bytesignature(*commandefaultargs)
                skip = command.neededparams
            else:
                valuestoappend = ParamType.rewrite(paramtype, paramdefault)
                
            sig += valuestoappend
        return sig
    
    
    def compile(self, *args):
        #print("+++++ Compiling Alias "+repr(self.getParam(0)))
        compiled = array('B')
        
        argstaken = 0
        paramstaken = 0
        params = self.params
        
        while paramstaken < len(params):
            p = params[paramstaken]
            paramstaken+=1

            ptype = p.ptype
            pvalue = p.defaultvalue
            if ptype == ParamType.command: #param type
                command = self.commands[pvalue.lower()]
                commandargs = []
                for i in range(0, command.neededparams):
                    value = params[paramstaken].defaultvalue
                    paramstaken += 1

                    if value == None:
                        value = args[argstaken]
                        argstaken += 1

                    else: #make sure value is a string
                        value = str(value)
                    
                    commandargs.append(value)
                
                #print(">>>> "+repr(commandargs))
                compiled.extend(command.compile(*commandargs))

            else:
                if pvalue == None:
                    value = args[argstaken]
                    argstaken += 1
                else:
                    value = pvalue

                for y in ParamType.rewrite(ptype, value):
                    compiled.append(y)
                
        return compiled

            
class Command(CodeCommand):
    def __init__(self, name, code, constants):
        '''Binary code which the command represents. Constants holds a list of
        all defines, i.e. constants.'''
        CodeCommand.__init__(self)
        self.name = name
        self.code = code
        self.constants = constants
        self.signature = [self.name]
    
    
    def addParam(self, paramtype, defaultvalue=None, definevaluestype=None, description=None):
        super().addParam(paramtype, defaultvalue, definevaluestype, description)
        if defaultvalue == None and paramtype != ParamType.eos:
            self.signature.append("$%d"%len(self.signature))

    
    def bytesignature(self, *args):
        '''Returns the commands byte signature. It is possible to
        set expected values, by providing an *args array with default values'''
        sig = [self.code]
        argstaken = 0
        for param in self.params:
            paramtype = param.ptype
            paramdefault = param.defaultvalue
            
            if paramdefault == None and argstaken < len(args):
                paramdefault = args[argstaken]
                argstaken += 1

            if paramdefault == None:
                valuestoappend = [''] * len(ParamType.rewrite(paramtype, 0))
            else:
                valuestoappend = ParamType.rewrite(paramtype, paramdefault)
            sig += valuestoappend
            
        return sig
        
        
    def compile(self, *args):
        #print("Compile "+repr(self.code)+" with args "+repr(args))
        self.checkParamscount(len(args))
             
        usedargs = 0
        
        bytes = array('B')
        bytes.append(self.code)
        
        for param in self.params:
            value = None
            if param.defaultvalue == None:
                value = args[usedargs]
                usedargs += 1
                
            else:
                value = param.defaultvalue

            try:
                value = toint(value)
            except: #value may not be an integer, but may be a (defined) constant!
                try:
                    value = value.lower()
                    if value in self.constants:
                        value = self.constants[value]
                    else:
                        raise Exception()
                except:
                    raise Exception("The given parameter could not be converted to integer and is also not defined as a constant: "+repr(value))
                
            bytes.fromstring(ParamType.rewrite(param.ptype, value))
        
        return bytes
        