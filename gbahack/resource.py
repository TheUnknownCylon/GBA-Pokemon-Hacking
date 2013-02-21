

class PointerObserver():
    '''
    Interface for classes that want to observe pointer changes.
    By calling register(), the object is registered for pointer changes updates,
    after such a change, the pointerChanged callback is called.
    '''
    
    def register(self, rm):
        '''
        Registers itself to the resource manager that the class
        want to get notifications of pointer changes.
        '''
        rm.register(self)
        
    
    def pointerChanged(self, rm, oldpointer, newpointer):
        '''Callback from resource manger rm: a pointer has changed.'''
        raise NotImplementedError()
    
    
    def pointerRemoved(self, rm, pointer):
        '''A pointer was removed from the ROM, and becomes an invalid resource.'''
        raise NotImplementedError()
    
        

class ResourceManager():
    '''Manager of ROM resources.'''
    
    def __init__(self, rom):
        self.rom = rom
        self.pointerwatchers = []
        
        #Keep resources in a list of resources, and a list of pointers
        self.resources = {}   #key: resource, value: pointer (None=no pointer)
        self.pointers = {}    #key: pointer,  value: resource (note: contians only ROM-stored resources)
    
    
    def register(self, pointerobserver):
        '''
        Register an PointerObserver object for pointer change callbacks.
        Registee should be of type PointerObserver.
        '''
        self.pointerwatchers.append(pointerobserver)
    
    
    def get(self, resourceclass, pointer):
        '''
        Returns an initialized resource, read from the rom.
        Resourceclass is the resource class that should be read.
        Pointer is the location in the ROM where the pointer is stored.
        '''
        if not pointer in self.pointers:
            r = resourceclass.read(self.rom, pointer)
            self.pointers[pointer] = r
            self.resources[r] = pointer
            
        elif not isinstance(self.pointers[pointer], resourceclass):
            raise Exception("Pointer already loaded, but of different resource type.")
        
        return self.pointers[pointer]
    
    
    def store(self, resource, allow_replacement=True):
        '''
        Stores a resource in the ROM.
        If the resource was not already stored, the resource is written into a
        new location in the ROM.
        If the resource was already stored the resource will be updated.
        If allow_replacement is False, the resource is *always* written at the
        old pointer location, possibly overwriting other data.
        If a pointer location changes, all pointerwachters are informed.
        
        Returns the new pointer location.
        '''
        oldpointer = None
        if resource not in self.resources:
            newpointer = resource.write(self.rom, 0x08000000)  #TODO: Hardcoded :(
        
        else:
            oldpointer = self.resources[resource]
            newpointer = resource.update(self.rom, oldpointer, allow_replacement)
            del self.pointers[oldpointer]
        
        self.pointers[newpointer] = resource
        self.resources[resource]  = newpointer
        
        #Inform others only after the resoure manager indices are up to date.
        if oldpointer and oldpointer != newpointer:
            print("! Pointer 0x%X has been changed 0x%X"%(oldpointer, newpointer))
            for watcher in self.pointerwachters:
                watcher.pointerChanged(self, oldpointer, newpointer)
        
        return newpointer
    
    
    def delete(self, resource):
        '''Removes a resource from the ROM and informs pointerwachters.'''
        if resource not in self.resources:
            return
        
        pointer = self.resources[resource]
        del self.resources[resource]
        del self.pointers[pointer]
        resource.delete(self.rom, pointer)
        
        print("! Pointer 0x%X is removed from the ROM."%pointer)
        for watcher in self.pointerwatchers:
            watcher.pointerRemoved(self, pointer)
        

class Resource():
    '''
    Abstract class that represents a resource in a given ROM.
    By implementing the read, and bytestringmethods, the developper gets
    write, update and delete method for free.
    
    This class does not deal with resources that depend of other resources,
    for that, these dependencies should be added to implementations of
    subclasses.
    '''
    
    name = "resource"
    
    @classmethod
    def read(cls, rom, pointer):
        '''
        Loads the resource from a rom, starting at a given pointer.
        Returns a new initialized Resource object.
        '''
        raise NotImplementedError()
     
    
    def bytestring(self):
        '''
        Returns the bytestring representation of the resource.
        This is how the resource should be written to the ROM (i.e. the compiled
        resource object). Returns an array.array('B') object.
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
        rom.trunc(pointer, old.blength())
        return old


    def blength(self):
        '''
        Returns the length of the resource in bytes.
        '''
        return len(self.bytestring())
        
    
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
        
        writebytes = self.bytestring()
        blength = len(writebytes)
        
        #Determine where to write the data to
        writepointer = pointer        
        if not force == True:
            writepointer = rom.findSpace(pointer, blength)
        
        rom.writeArray(writepointer, writebytes)

        return writepointer
            
    
    def update(self, rom, pointer, force=False):
        '''
        Updates the given resource in the rom. If the new resource is larger
        than the old one, the old data is removed, and the object is written
        at another location in the ROM. If the resource is smaller than the old
        one, the unused bytes are freed.
        '''
        old = self.delete(rom, pointer)
        
        if self.blength() <= old.blength():
            return self.write(rom, pointer, force=True)
        else:
            return self.write(rom, pointer, force)
         
