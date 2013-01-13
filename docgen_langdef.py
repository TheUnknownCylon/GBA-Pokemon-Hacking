'''
This file contains a simple docs generator, it lists all
possible PokeScript information and generates a markdown file
for further reference.
'''

import os
from gbahackpkmn.pokescript import ScriptLang
from gbahackpkmn.pokescript.langcommands import ParamType

def ptype_to_text(ptype):
    if ptype == ParamType.byte: return "byte"
    elif ptype == ParamType.word: return "word"
    elif ptype == ParamType.int: return "int"
    elif ptype == ParamType.pointer: return "pointer"
    elif ptype == ParamType.eos: return "eos"
    elif ptype == ParamType.command: return "command"
    elif ptype == ParamType.pointer_text: return "Pointer to String"
    elif ptype == ParamType.pointer_movement: return "Pointer to Movement"
    else: return "0x%X"%ptype


def alias_to_text(alias):
    t = ""
    i = 0
    for sigpart in alias.signature:
        if sigpart[0]=="$":
            t += "<arg%d> "%i
            i += 1
        else:
            t += "%s "%sigpart
    return t

def generate(sublang, gamenames, f):
    langdef = ScriptLang(sublang=sublang)
    
    commands = langdef.getCommands()
    command_names = sorted(commands.keys())
    aliases = langdef.getAliases()
    
    f.write("# PokeScript Description for %s\n"%gamenames)
    f.write("This document lists all the commands and aliases for the default PokeScript %s lanague.\n\n"%gamenames)
    f.write("__Note:__ This document is automatically generated based on the script langdefinitions.\n\n")

    f.write("## List of commands\n")
    for command in command_names:
        f.write("`%s` "%command)
    f.write("\n\n")
    
    f.write("## List of aliasses\n")
    f.write("An alias is a shortcort for common used constructions of command sequences. ")
    f.write("In PokeScript aliases can be used, as well as normal commands.")
    for alias in aliases:
        f.write("* `%s`\n"%alias_to_text(alias))
    f.write("\n\n")
    
    #Parse each command, write down its name, description and arguments
    f.write("## Commands in detail\n\n")
    for command_name in command_names:
        
        #Main command and usage
        command = commands[command_name]
        t  = "### %s (0x%X)\n"%(command_name, command.code)
        t += "__Description__: %s  \n"%(command.getDescription() or "_No description_")
        t += "__Usage__: `%s "%command_name
        
        #Arguments section
        argsdesc = "__Argments__:  \n"
        for i in range(0, command.getNumberOfParams()):
            ptype, _ = command.getParam(i)
            
            t += '<arg%d> '%i
            argsdesc += "    `%s` `<arg%d>`: "%(ptype_to_text(ptype), i)
            argsdesc += "%s  \n"%(command.getArgDescription(i) or "_No description_")
        t += "`  \n"
        if command.getNumberOfParams() > 0:
            t += "%s  \n"%argsdesc
        t += "\n\n"
        f.write(t)
        
    f.write("## Aliasses in detail\n\n")
    for alias in aliases:
        t = "### Alias `%s`\n"%alias_to_text(alias)
        t += "__Usage__: `%s`  \n"%alias_to_text(alias)
        t += "__Description__: %s  \n"%(alias.getDescription() or "_No description_")
        
        argsdesc = "__Argments__:  \n"
        
        i = 0
        for paramindex in range(0, len(alias.params)):
            ptype, default = alias.getParam(paramindex)
            if default == None:
                argsdesc += "    `%s` `<arg%d>`: "%(ptype_to_text(ptype), i)
                argsdesc += "%s  \n"%(alias.getArgDescription(paramindex) or "_No description_")
                i += 1
        
        t += "%s\n"%argsdesc
        f.write(t)
        
    
sublangs = {
    'rs':'Ruby and Sapphire',
    'e':'Emerald',
    'frlg':'FireRed and LeafGreen'
}

for sublang in sublangs.keys():
    f = open(os.path.join('docs', 'pokescript', "%s.md"%sublang), 'w')
    generate(sublang, sublangs[sublang], f)
    f.close()
    print("Generated doc %s"%f.name)
    