

from gbahackpkmn.pokescript.ast import ASTRef, ASTCollector

def analyzeScript(scriptgroup):
    '''
    Method that analyzes a whole scriptgroup for errors and warnings.
    Returns two lists: warnings and errors.
    '''
    
    errors = []
    warnings = []

    brokenrefsfinder = FindBrokenRefs(scriptgroup.getPointerlist(), errors)
    
    #Look up if there is a $start
    if not scriptgroup.has('$start'):
        errors.append((None, "There is no $start in the script."))
    
    #Check all AST Nodes for warnings and errors
    for astnode in scriptgroup.getASTNodes():
        astnode.collectFromASTs([brokenrefsfinder])
        
    return warnings, errors
    

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

