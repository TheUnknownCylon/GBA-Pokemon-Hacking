try: import png
except: print("PyPNG could not be loaded, using the method toPNG() will fail!.")


def readSprite(rom, pointer, width, height): 
  '''Reads a sprite at the given pointer from the ROM.
  It returns a matrix containing palette indices.
  
  NOTE: Only 16 color sprites are supported.'''
  
  w = width
  h = height
  p = pointer
  
  spritesize = int( (w * h) / 2 )  # /2: we are dealing with nibles, not bytes
  blob = rom.readBytes(p, spritesize)[1]
  
  #rewrite the blob to a multidimensional array representing the image
  # The image is build up from 8x8 pixel blocks
  
  matrix = [[0 for col in range(w)] for row in range(h)]

  numblocksinw = int(w / 8)
  numblocksinh = int(h / 8)
    
  #first read block 0,0; then 0,1; 0,n; 1,0; 1, 1; ... etc
  pointer = 0 #pointer reading in the actual blob
    
  for bh in range(0, numblocksinh):
    for bw in range(0, numblocksinw):
      pmh = bh * 8 
      #read 8 pixels * 16 pixels (note: 1 byte in blob = 2 pixels)
      for ph in range(0, 8):
        pmw = bw * 8
        for pw in range(0, 4):
          pixels = blob[pointer]
          pixel_left = pixels & 0x0F
          pixel_right  = pixels >> 4
          
          matrix[pmh][pmw] = pixel_left
          matrix[pmh][pmw+1] = pixel_right
            
          pointer += 1
          pmw += 2
        pmh += 1
        
  return matrix

def toPNG(f, matrix, palette):
  '''Rewrites a given matrix (which can be the output of readSprite), to a PNG
  file. A palette should be a Palette object which could be 
  
  Note: PyPNG (https://github.com/drj11/pypng/) is required.'''
  
  #Rewrite the palette object to a PNG-palette
  p = palette.aslist()
  
  #write the matrix to the file-object
  w = png.Writer(len(matrix[0]), len(matrix), palette=p)
  w.write(f, matrix)
  
  