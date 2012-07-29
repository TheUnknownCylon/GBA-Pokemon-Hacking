
'''
Nice way to evaluate mathematical expressions which are expressed as a string.

Code copied, and adjusted to support varrefs, from:
  http://stackoverflow.com/questions/2371436/evaluating-a-mathematical-expression-in-a-string
'''

import ast
import operator as op

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor}

def eval_expr(expr, varset):
    """
    >>> eval_expr('2^6', {})
    4
    >>> eval_expr('2**6', {})
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)', {})
    -5.0
    """
    return eval_(ast.parse(expr).body[0].value, varset) # Module(body=[Expr(value=...)])

def eval_(node, varset):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.operator): # <operator>
        return operators[type(node)]
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return eval_(node.op, varset)(eval_(node.left, varset), eval_(node.right, varset))
    elif isinstance(node, ast.Name): # <varref>
        if node.id in varset: return varset[node.id]
    else:
        raise TypeError(node)
      
