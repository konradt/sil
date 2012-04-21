import copy
from ast import Node
from structures import *

class Evaluator():

    def __init__(self):
        self.__variables = { }
        self.__functions = Map()
        self.toReturn = False
    
    def visit(self, ast):
        if ast.type == "selection":
            print ast.type
            return self.visit_Select(ast)
        if ast.type == "assignment":
            print ast.type
            return self.visit_Assign(ast)
        if ast.type == "ifelse":
            print ast.type
            return self.visit_IfThenElse(ast)
        if ast.type == "relexpr":
            print ast.type
            return self.visit_RelExpr(ast)
        if ast.type == "boolean":
            print ast.type
            return self.visit_Boolean(ast)
        if ast.type == "integer":
            print ast.type
            return self.visit_Integer(ast)
        if ast.type == "unaryop":
            print ast.type
            return self.visit_UnaryOp(ast)
        if ast.type == "binaryop":
            print ast.type
            return self.visit_BinaryOp(ast)
        if ast.type == "while":
            print ast.type
            return self.visit_While(ast)
        if ast.type == "block":
            print ast.type
            return self.visit_Block(ast)
        if ast.type == "funcdef":
            print ast.type
            return self.visit_FuncDef(ast)
        if ast.type == "print":
            print ast.type
            return self.visit_Print(ast.args)
        if ast.type == "funccall":
            print ast.type
            return self.visit_FuncCall(ast)
        if ast.type == "return":
            print ast.type
            return self.visit_Return(ast)
        
    def visit_Return(self, node):
        return self.visit(node.value)
    
    def visit_Print(self, node):
        if isinstance(node, Node):
            print self.visit(node.arg),
        else:
            print node
        if node.nextArgs:
            self.visit_Print(node.nextArgs)
        else:
            print
    
    def visit_FuncDef(self, node):
        self.__functions.add(node.name, node.args, node.body)
    
    def visit_FuncCall(self, node):
        tmpVariables = copy.deepcopy(self.__variables)
        tmpFunctions = copy.deepcopy(self.__functions)
        #dostajemy wszystkie definicje funkcji zwiazanych z dana nazwa, pozniej musimy sprawdzic zmienne czy sa odpowiedniego typu
        defList = self.__functions.get(node.name)
        possibleToUse = []
        for definition in defList:
            #definition[1] to jest lokalizacja argumentow w krotce
            if len(definition[1]) == len(node.args):
                bestFits = True
                i = 0;
                metric = 0.0;
                #lecimy po wszystkich argumentach i sprawdzamy czy da sie rzutowac, jesli nie to przerywamy petle
                while i < len(definition[1]):
                    if definition[1][i][0] == node.args[i].type:
                        print "zgadza sie"
                        metric += 1.
                    elif definition[1][i][0] == 'int' and node.args[i].type == 'float':
                        bestFits = False
                        metric += 0.9
                        print "rzutowanie float na int"
                    elif definition[1][i][0] == 'float' and node.args[i].type == 'int':
                        bestFits = False
                        metric += 0.45
                        print "rzutowanie int na float"
                    elif definition[1][i][0] == 'bool' and node.args[i].type == 'int':
                        bestFits = False
                        metric += 0.8
                        print "rzutowanie int na bool"
                    elif definition[1][i][0] == 'bool' and node.args[i].type == 'float':
                        bestFits = False
                        metric += 0.7
                        print "rzutowanie float na bool"
                    else:
                        break
                    i = i+1
                    
                #jesli mamy best fita, to super
                if bestFits:
                    possibleToUse = definition
                    break
                #dodajemy do listy w postaci elementu slownika {wartosc_metryki : definicja}
                possibleToUse.append(tuple([metric, definition]))
        #musimy teraz posortowac od razu odwrotnie, zeby wziac pierwszy element (rownie dobrze mozemy wziac ostatni, ale tak jest bardziej intuicyjnie)
        print possibleToUse
        
        if isinstance(possibleToUse, list):
            possibleToUse = sorted(possibleToUse, key=lambda item: item[0], reverse=True)
            definition = possibleToUse[0][1]
            print "tutaj"
        else:
            definition = possibleToUse
            print len(possibleToUse[1])
        
        i = 0
        print definition
        print definition[1], len(definition[1])
        while i < len(definition[1]):
            print definition[1][i], node.args[i].value
            self.__variables[definition[1][i][1]] = self.assign_with_cast(definition[1][i][0], node.args[i].value)
            i =+ 1
            
        result = self.visit(definition[2])
        
        self.__functions = copy.deepcopy(tmpFunctions)
        self.__variables = copy.deepcopy(tmpVariables)
        
        return result
        #=======================================================================
        # definition = self.__variables[node.name]
        # defArgs = definition.args
        # callArgs = node.args
        # if defArgs.arg:
        #    self.__variables[defArgs.arg] = self.visit(callArgs.arg)
        #    print self.__variables
        # while defArgs.nextArgs:
        #    defArgs = defArgs.nextArgs
        #    callArgs = callArgs.nextArgs
        #    self.__variables[defArgs.arg] = self.visit(callArgs.arg)
        # result = self.visit(definition.body)
        # self.__variables = copy.deepcopy(tmpVariables)
        # return result
        #=======================================================================
    
    def visit_Block(self, node):
        for item in node.stmts:
            result = self.visit(item)
        return result
    
    def visit_While(self, node):
        while ( self.visit(node.cond) ):
            x = self.visit(node.body)
            if x:
                return x
        return
    
    def visit_Assign(self, node):
        self.__variables[node.name] = self.visit(node.value)
        print self.__variables
        return
    
    def visit_Select(self, node):
        return self.__variables[node.name]
        #=======================================================================
        # result = self.__variables[node.name]
        # if self.toReturn:
        #    print "byla funckja :-)"
        #    self.__variables = copy.deepcopy(self.tmpNames)
        #    self.tmpNames = None
        # return result
        #=======================================================================
        
    
    def visit_RelExpr(self, node):
        if node.op == '==':
            return self.visit(node.left) == self.visit(node.right)
        elif node.op == '!=':
            return self.visit(node.left) != self.visit(node.right)
        elif node.op == '>':
            return self.visit(node.left) > self.visit(node.right)
        elif node.op == '<':
            return self.visit(node.left) < self.visit(node.right)
        elif node.op == '>=':
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op == '<=':
            return self.visit(node.left) <= self.visit(node.right)
        
    def visit_BinaryOp(self, node):
        if node.op == '+':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == '-':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == '*':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == '/':
            return self.visit(node.left) / self.visit(node.right)
        
    def visit_UnaryOp(self, node):
        if node.op == '-':
            return -(self.visit(node.expr))

    def visit_Integer(self, node):
        return node.value
    
    def visit_Boolean(self, node):
        return bool(node.value)
    
    def visit_IfThenElse(self, node):
        if self.visit(node.cond):
            return self.visit(node.ifTrue)
        elif node.ifFalse:
            return self.visit(node.ifFalse)
    
    def printAst(self, ast):
        print ast.expr
        
    def assign_with_cast(self, castTo, value):
        if castTo == 'int':
            return int(value)
        if castTo == 'float':
            return float(value)
        if castTo == 'bool':
            return bool(value)
        if castTo == 'string':
            return str(value)