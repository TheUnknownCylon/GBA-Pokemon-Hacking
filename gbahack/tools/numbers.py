 
def toint(v):
  '''Tries to convert a value to int if possible.
  Possible decodings are just the integer as string or int,
   or a hex-string: toint("#10"), will return 0x10 (or 16)'''
  try: return int(v)
  except: pass
  
  try: v = v.strip()
  except: pass
  
  if len(v) > 1 and v[0] == '#':
    try: return int('0x'+v[1:], 16)
    except: pass
  
  if len(v) > 2 and v[0:2].lower() == '0x':
    try: return int(v, 16)
    except: pass
    
  if len(v) > 2 and v[0:2].lower() == '&h':
    try: return int(v[2:], 16)
    except: pass
    
  raise Exception("Could not convert value to number: "+repr(v))