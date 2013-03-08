
class ScriptBurner():
    '''
    Writes a scriptgroup to ROM.
    TODO: Currently lets write resources directly to the ROM, but
          this should actually be done by the resource manager.
          In that way, pointer changes can be handeld properly by others.
          Therefore, this ScriptBurner needs an update.
    '''
  
    def __init__(self, rom):
        self.rom = rom
  
  
    def burn(self, scriptgroup):
        '''
        This method writes a scriptgroup to the ROM.
        Pointers on where resources should be stored should be set in the scriptgroup.
        If a scriptgroup pointer is None, a new location will be set.
        If a resource does not fit into the given location, it will be placed at a
        new location in the ROM.
        
        Important!
        Always make sure that the scriptgroup has up to date pointers.
        
        '''
        #TODO: Possible improvement, delete all first, then write
        
        #Note: Burning is a two phase process. First round, pointers are not set.
        #      After round one, the correct pointers are known.
        #      Second round, rewrite with correct pointers.
        
        rom = self.rom
        if 'freespace' in rom.metadata:
            startpointer = rom.metadata.freespace
        else:
            startpointer = 0x00800000
        
        oldpointers = scriptgroup.getPointerlist()        
        
        #Keep a list of all assigned pointers to a var.
        newpointers = {}
        
        #First pass
        print("---> pass 1")
        for name, (resource, oldpointer) in scriptgroup.getAll().items():
            try:
                resource.setPointerlist(oldpointers)
            except:
                pass
            
            if oldpointer == None:
                #Do not update, but write at new location
                newpointer = resource.write(rom, startpointer)
                newpointers[name] = newpointer
                
            else:
                #A pointer was set, try to update the resource
                newpointer = resource.update(rom, oldpointer, writeoffset=startpointer)
                newpointers[name] = newpointer
                
            scriptgroup.setPointer(name, newpointer)

        #Second pass
        print("---> pass 2")
        for name, (resource, oldpointer) in scriptgroup.getAll().items():
            try:
                resource.setPointerlist(newpointers)
            except:
                pass
            
            #Do not update, but write at new location
            resource.write(rom, newpointers[name], force=True)
        
        
        return newpointers
