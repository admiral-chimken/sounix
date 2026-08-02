import ast

import operator


OPS = {
  
     ast.Add: operator.add,
    
     ast.Sub: operator.sub,

     ast.Mult: operator.mul,

     ast.Div: operator.truediv,

     ast.Mod: operator.mod,

     ast.Pow: operator.pow,

     ast.USub: operator.neg,
}



def _eval(node):
    if isinstance(node, ast.Constant):

       return node.value

    if isinstance(node, ast.BinOp):
 
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))

    if isinstance(node, ast.UnaryOp):

        return OPS[type(node.op)](_eval(node.operand))

    raise ValueError("invalid expression")

def calculate(expression):
    
    tree = ast.parse(expression,mode="eval")
    return _eval(tree.body)
