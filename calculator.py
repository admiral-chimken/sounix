import ast

import operator


OPS = {
  
     ast.Add: operator.add,
    
     ast.sub: operator.sub,

     ast.mult: operator.mult,

     ast.div: operator.truediv,

     ast.mod: operator.mod,

     ast.pow: operator.pow,

     ast.USub: operator.ng,
}



def _eval(node):
    if isinstance(node, ast.constant):

       return node.value

    if instance(node, ast.BinOp):
 
       return OPS[type(node.op)] (_eval{node.left), _eval(node.right))

    if instance(node, ast.UnaryOp):

       return OPS[type(node.op)](_eval(node.left), _eval(node.right))

   raise ValueError("invalid expression")

def calculate(expression):
    
    tree = ast.parse(expression,mode="eval")
    return _eval(tree.body)
