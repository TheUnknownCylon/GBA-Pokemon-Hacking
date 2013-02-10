

from gbahackpkmn.pokescript.ast import ASTRef, ASTCommand, ASTRoutine, ASTCollector

def analyzeScript(scriptgroup):
    '''
    Method that analyzes a whole scriptgroup for errors and warnings.
    Returns two lists: warnings and errors.
    '''
    
    errors = []
    warnings = []

    brokenrefsfinder = FindBrokenRefs(scriptgroup.getPointerlist(), errors)
    argsvalidtor = ValidateArguments(errors)
    invalidends = FindScriptsWithoutEnd(errors)
    
    #Look up if there is a $start
    if not scriptgroup.has('$start'):
        errors.append((None, "There is no $start in the script."))
    
    #Check all AST Nodes for warnings and errors
    for astnode in scriptgroup.getASTNodes():
        astnode.collectFromASTs([brokenrefsfinder, argsvalidtor, invalidends])
        
    return warnings, errors
    

class ValidateArguments(ASTCollector):
    '''Collector that checks whether all given arguments adhere to the
    parameter settings.'''
    
    def __init__(self, errorslist):
        self.errors = errorslist
    
    def collect(self, astnode):
        if isinstance(astnode, ASTCommand):
            errors = astnode.validateArgs()
            for error in errors:
                self.errors.append((astnode, error))
            

class FindBrokenRefs(ASTCollector):
    '''Collector that searches for used but not defined varnames.'''
    
    def __init__(self, varnames, errorslist):
        '''Initialze with a dict of available k:varnames v:pointer.'''
        self.varnames = varnames
        self.errors = errorslist
        
    def collect(self, astnode):
        if isinstance(astnode, ASTRef):
            if astnode.getRef() not in self.varnames.keys():
                self.errors.append((astnode, "No variable: %s"%astnode.getRef()))


class FindScriptsWithoutEnd(ASTCollector):
    '''Scripts without a valid ending are dangerous. The game crashes,
    but a next decompile of the script fails. Therefore its better to make sure
    that the end of an script is enforced.'''
    
    def __init__(self, errorslist):
        self.errors = errorslist
    
    def collect(self, astnode):
        if isinstance(astnode, ASTRoutine):
            if not astnode.hasEnd():
                self.errors.append((astnode, "This routine has no end. Each routine should have a valid end (i.e. each script should end with one of the following commands: `end`, `return`, `jump`, or `jumpstd`)."))
    
    