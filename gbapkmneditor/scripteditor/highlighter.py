from PyQt4.QtGui import *
from PyQt4.QtCore import *

class HighlightingRule():
  def __init__( self, pattern, format ):
    self.pattern = pattern
    self.format = format


class PokeScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        
        self.parent = parent
        self.highlightingRules = []
        
        begin   = "^( |\t)*" #At the beginning of a string, layout allowed.
        newelem = "(^|\s)"   #Beginning of the line or any whitespace char.
        
        resourcedef_st = QTextCharFormat()
        resourcedef_st.setFontWeight(QFont.Bold)
        resourcedef = HighlightingRule(QRegExp(begin+"\#(.)+"), resourcedef_st)
        
        comment_st =  QTextCharFormat()
        comment_st.setForeground(Qt.darkGreen)
        self.comment_st = comment_st
        
        number_st = QTextCharFormat()
        number_st.setForeground(Qt.darkBlue)
        hexval = HighlightingRule(QRegExp(newelem+"0x[0-9A-Fa-f]+[\s]"), number_st)
        number = HighlightingRule(QRegExp(newelem+"[0-9]+[\s]"), number_st)
        
        scriptvar_st = QTextCharFormat()
        scriptvar_st.setForeground(Qt.red)
        scriptvar = HighlightingRule(QRegExp(newelem+"\$(\S)+"), scriptvar_st)
        
        typeintro_st = QTextCharFormat()
        typeintro_st.setForeground(Qt.darkGray)
        typeintro = HighlightingRule(QRegExp(begin+"(:|=)"), typeintro_st)
        
        self.highlightingRules.append(resourcedef)
        self.highlightingRules.append(hexval)
        self.highlightingRules.append(number)
        self.highlightingRules.append(scriptvar)
        self.highlightingRules.append(typeintro)

    
    def highlightBlock(self, text):
        '''Highlights a text-block in the script.'''
        
        text = self.removecomment(text, 0)

        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = expression.indexIn(text, index+1)
        self.setCurrentBlockState(0)
        

    def removecomment(self, text, offset):
        '''Parser helper, removes comments from the string, so that comments
        will not be processed. Also marks them as comment in the editor.'''
        
        #dirty check, if string starts with =, there is no comments support
        try:
            if text.lstrip()[0] == "=":
                return text
        except:
            pass
        
        index = text.find("'", offset)
        if index == -1:
            return text
        elif index>0 and text[index-1] == "\\":
            return self.removecomment(text, index+1)
        else:
            self.setFormat(index, len(text)-index, self.comment_st)
            if index > 0:
                return text[:index-1]
            else:
                return ""
        