"""
This file contains some tools of reading and writing .s files.
.s files are ARM assembly code. It is aimed to be compatible with the Nintendo
mid2agb compiler. Mid2Agb tool is capable of converting MIDI files to ARM code,
is .s format. This tool takes it further from here, and converts the .s file to
ARM binary bytecode.

  !! IMPORTANT NOTE: Note that this file does not convert real assembly code as
                     it has been written to be compatible with the output of the
                     mid2agb compiler of Nintendo
                     
                     Since I could not find a good tool written in python, which
                     does compiling ARM assembly correctly, I came up with this
                     quick, but not 100% compilant, implementation.
                     
  In this implementation
   * All instructions should be on a separate line.
   * Labels should be on a separate line, directly followed by a ":"
   * Indention of commands is not required, but allowed.
   * Implemented instructions are .equ .byte .word .include .end
   * After each instruction a tab ("\t") is expected
   *  -> One exception, after include a space is expected: include "Filename"
   * Comments can be started with @, and ends at the end of a line
   * Defines (.equ) and labels are in the format: [A-Za-z][A-Za-z0-9]*
   
  
"""

#TODO: Implement other .s parsing mechanism, this one feels a bit clooney
import os
import struct
from array import array

from gbahack.tools import mathexp

class EndOfParsing(Exception):
  pass

class SReader():
  def __init__(self, sourcefile):
    self.output = array('B')
    
    self.globalvars = []
    self.defines = {}
    self.openfiles = []
    try: self.parsefile(sourcefile)
    except EndOfParsing as e: pass
    except Exception as e: raise e

    
  def getBytes(self):
    '''Returns the read song in a byte-array.'''
    return self.output
    
  def parsefile(self, file):
    '''Parsers a file, line by line.'''
    
    #Change directory so we can take includes relative from the file.
    # After the file is parsed, the directory is restored to the current working directory
    
    mypath = os.getcwd()
    try: os.chdir(os.path.dirname(file))
    except: pass #take the error when opening the file
    
    try:
      for line in open(file, 'r'): self._handle(line)
    except Exception as e: raise
    finally: os.chdir(mypath)
      
  def getGlobalKeys(self):
    '''Returns a list of all global variables.'''
    return self.globalvars
      
      
  def getDefined(self, key):
    '''Returns the value for a global definition.'''
    if key not in self.globalvars:
      raise Exception("No such global variable: %s"%key)
    return self.defines[key]
    
  
  def exp(self, expr={}):
    '''Evaluates a mathematical expression, all defines can be passed
    as varrefs in the expr variable. Returns always an integer'''
    value = mathexp.eval_expr(expr, self.defines)
    if value == None:
      raise Exception("Error in .s file, could not evaluate: %s."%expr)
    return int(value)
  
  
  def _handle(self, line):
    #Remove human readable mess, split command and parameters
    lineinfo = line.strip().split("@")[0].split("\t", 1)
    if len(lineinfo) == 0: return
    
    command = lineinfo[0].split(" ")[0]
    try: commandarg = lineinfo[0].split(" ")[1]
    except: commandarg = None
    if len(command) == 0: return

    param   = None
    if len(lineinfo) > 1: param = lineinfo[1]
    
    if   command == ".equ":  self._handle_equ(param)
    elif command == ".byte": self._handle_byte(param)
    elif command == ".word": self._handle_word(param)
    elif command == ".include": self._handle_include(commandarg)
    elif command[-1] == ":" and param == None: self._handle_label(command[:-1])
    elif command == ".global":  self._handle_global(param)

    elif command == ".section": pass 
    elif command == ".align":   pass
    elif command == ".end":     raise EndOfParsing("hkjh")
    
    else: print ("Unknown command to parse: %s" %command)

    
      
  def _handle_equ(self, param):
    keyword = param.split(",")[0].strip()
    value   = self.exp(param.split(",")[1].strip())
    if keyword in self.defines:
      print ("%s is already defined! Overwiting!" %keyword)
    self.defines[keyword] = value
    
  def _handle_byte(self, param):
    values = list(map(lambda x: x.strip(), param.split(",")))
    for value in values:
      self.output.fromstring(struct.pack("<B", self.exp(value)))
  
  def _handle_word(self, param):
    values = list(map(lambda x: x.strip(), param.split(",")))
    for value in values:
      self.output.fromstring(struct.pack("<I", self.exp(value)))
      
  def _handle_label(self, label):
    self._handle(".equ\t%s,%s"%(label,repr(len(self.output))))
      
  def _handle_include(self, param):
    if param == None:
      raise Exception(".include requires a filename between "", example: .include \"myfile.s\"") 
    
    values = list(map(lambda x: x.strip(), param.split(",")))
    for value in values:
      try: self.parsefile(value[1:-1])
      except IOError as e: raise IOError("Could not no find or open include %s"%value)
    
  def _handle_global(self, param):
    values = list(map(lambda x: x.strip(), param.split(",")))
    for value in values:
      self.globalvars.append(value)
  
