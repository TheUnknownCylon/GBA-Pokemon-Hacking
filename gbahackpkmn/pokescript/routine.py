
from gbahack import Resource
from gbahack.resource import PointerObserver
from gbahackpkmn.pokescript.ast import ASTCommand, ASTRoutine

class Routine(Resource, PointerObserver):
    '''
    Game routine object.
    '''
    
    name = "script"
    
    def __init__(self, resourcemanager=None, asttree=None, pointerlist=None):
        '''
        Initializes the routine object.
        A routine should always be able to depend on other resources, and
        therefore takes a resourcemanager as argument.
        
        Takes a full AST tree as arguments.
        '''
        if asttree == None:
            asttree = []
        if pointerlist == None:
            pointerlist = {}
        
        self.asttree = asttree
        self.pointerlist = pointerlist
        
        if resourcemanager:
            self.register(resourcemanager)
    
    
    def ast(self):
        '''Returns all ast subnodes as a list.'''
        return self.asttree
    
    
    def setPointerlist(self, pointerlist):
        '''
        Sets a list of variable names to pointers.
        Required for encoding
        '''
        self.pointerlist = pointerlist
    
    
    @classmethod
    def read(self, rom, pointer):
        '''
        Decompiles a script from the ROM, starting at a given pointer.
        Returns a new Routine instance, and a list of pointer-type references
        to which this routine points.
        '''
        
        asttree = []  #Abstract syntax tree holding all script nodes.

        #TODO: Smelly, cyclic import...
        from gbahackpkmn.pokescript.decompiler import CommandDecompiler
        decompiler = CommandDecompiler(rom.getScriptLang())
        
        p = pointer
        while True:
            try:
                p, astnode, _ = decompiler.decompileCommand(rom, p)
                asttree.append(astnode)
                
                if isinstance(astnode, ASTCommand) and astnode.code.endofscript:
                    break
            
            except Exception as e:
                print("Decoding routine failed: ")
                print(repr(e))
                raise e
            
        return Routine(rom.getRM(), asttree)
    
    
    def bytestring(self):
        '''Compiles the given routine into pokescript bytecode.'''
        return ASTRoutine("", self.asttree).encode(self.pointerlist)


    def pointerChanged(self, rm, old, new):
        '''Notification that a pointer has changed.'''
        print(" Routine: pointer has changed.")
    
    
    def pointerRemoved(self, rm, pointer):
        '''Notification that a pointer has been removed.'''
        print(" Routine: pointer removed.")
    
    
    def linkedPointers(self):
        '''Returns a list of pointers to which this resource links to.'''
        pointers = []
        for node in self.asttree:
            for ptuple in node.linkedPointers():
                pointers.append(ptuple)
        return pointers
    
    