 
'''
Very simpel configuration tool.
Supports config files of the following format:
  KEY=VALUE

Note that internally all keys are converted to lowercase.
All keys and values are stripped of layout chars (leading and trailing spaces
and tabs are removed)
'''

def getConfig(filename):
    '''
    Returns a config dict, read from filename.
    Each call to this method will re-read the file from disk.
    
    Returns an exception if reading the config fails.
    '''
    
    #Not cached in mem, return a new copy.
    myconf = {}
    for line in open(filename, 'r'):
        key, value = line.split("=", 1)
        myconf[key.strip().lower()] = value.strip()
    
    return myconf
