 
class Resource():
    '''
    Abstract class that represents a resource in a given ROM.
    By implementing the read, and bytestringmethods, the developper gets
    write, update and delete method for free.
    
    This class does not deal with resources that depend of other resources,
    for that, these dependencies should be added to implementations of
    subclasses.
    '''
    
    @classmethod
    def read(self, rom, pointer):
        '''
        Loads the resource from a rom, starting at a given pointer.
        Returns a new initialized Resource object.
        '''
        raise NotImplementedError()
     
    
    def bytestring(self):
        '''
        Returns the bytestring representation of the resource.
        This is how the resource should be written to the ROM (i.e. the compiled
        resource object)
        '''
        raise NotImplementedError()
        
        
    
    ### End of unimplemented methods ##
    
    
    @classmethod
    def delete(self, rom, pointer):
        '''
        Removes a resource of the implemented resource type from the ROM,
        frees the memory in the rom and returns the removed object.
        '''
        old = self.read(rom, pointer)
        rom.trunc(pointer, old.blength)
        return old


    def blength(self):
        '''
        Returns the length of the resource in bytes.
        '''
        len(self.bytestring())
        
    
    def write(self, rom, pointer=None, force=False):
        '''
        Writes the given resource to the rom, at the given pointer.
        If there is not enough free space left at the given pointer:
          1) and force==False, then the object is written at some free space.
          2) and force==True, the objects is written anyway, possibly 
             overwriting other excisting data. Pointer should contain a valid
             value.
             
        If a resource has to be overwritten, it should be removed first.
        
        Returns the pointer the resource was written to.
        Note that this pointer does not have to match the requested pointer.
        '''
        #Assertions checking first
        if force == True and not pointer:
            raise Exception("Write to ROM: force is true, but no pointer was given.")
        
        bytes = self.bytestring()
        blength = len(bytes)
        
        #Determine where to write the data to
        writepointer = pointer        
        if not force == True:
            writepointer = rom.findSpace(pointer, blength)
        
        rom.write(pointer, bytes)            

        return writepointer
            
    
    def update(self, rom, pointer, force=False):
        '''
        Updates the given resource in the rom. If the new resource is larger
        than the old one, the old data is removed, and the object is written
        at another location in the ROM. If the resource is smaller than the old
        one, the unused bytes are freed.
        '''
        old = self.delete(rom, pointer)
        if old.blength() <= self.blength():
            self.write(rom, pointer, force=True)
        else:
            self.write(rom, pointer, force)
            
   
