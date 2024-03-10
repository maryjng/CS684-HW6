import ast
import astor
import sys
import copy
from random import *
import random

def parse_target_program(path):
    # Parse the target program to AST
    source = open(path).read()
    return ast.parse(source, path)


class CountCompare(ast.NodeTransformer):
    # Count comparison operations in the AST
    def visit_Compare(self, node):
        global number_of_comparisons 

        if(isinstance(node.ops[0], ast.GtE)):
            new_node = ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators)
            number_of_comparisons += 1
        elif(isinstance(node.ops[0], ast.LtE)):
            new_node = ast.Compare(left=node.left, ops=[ast.Gt()], comparators=node.comparators)
            number_of_comparisons += 1
        elif(isinstance(node.ops[0], ast.Gt)):
            new_node = ast.Compare(left=node.left, ops=[ast.LtE()], comparators=node.comparators)
            number_of_comparisons += 1
        elif(isinstance(node.ops[0], ast.Lt)):
            new_node = ast.Compare(left=node.left, ops=[ast.GtE()], comparators=node.comparators)
            number_of_comparisons += 1

        return node

class CountBinaryOp(ast.NodeTransformer):
    # Count binary operations in the AST
    def visit_BinOp(self, node):
        global number_of_binary

        if(isinstance(node.op, ast.Add)):
            number_of_binary += 1
        elif(isinstance(node.op, ast.Sub)):
            number_of_binary += 1
        elif(isinstance(node.op, ast.Mult)):
            number_of_binary += 1
        elif(isinstance(node.op, ast.Div)):
            number_of_binary += 1

        return node

       
        

class CountFunctionCall(ast.NodeTransformer):
    # Count function calls in the AST
    def visit_If(self, node):
        global if_found 
        if_found = 1
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        #print("function_call line: ", node.lineno)
        global number_of_call, if_found
        if(if_found == 1):
            if_found = 0
            return node
        number_of_call += 1
        return node

    def visit_Assign(self, node):
        # Count assignments in the AST
        global number_of_assign
        number_of_assign += 1
        return node

    

class RewriteCompare(ast.NodeTransformer):
    # Rewrite comparison operations in the AST
    def visit_Compare(self, node):

        global visit_count, visit_target
        visit_count += 1
        if(visit_count == visit_target):
            ##print("Rewrite compare Line: ", node.lineno)
            if(isinstance(node.ops[0], ast.GtE)):
                new_node = ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators)
                return new_node
            elif(isinstance(node.ops[0], ast.LtE)):
                new_node = ast.Compare(left=node.left, ops=[ast.Gt()], comparators=node.comparators)
                return new_node
            elif(isinstance(node.ops[0], ast.Gt)):
                new_node = ast.Compare(left=node.left, ops=[ast.LtE()], comparators=node.comparators)
                return new_node
            elif(isinstance(node.ops[0], ast.Lt)):
                new_node = ast.Compare(left=node.left, ops=[ast.GtE()], comparators=node.comparators)
                return new_node

        return node

class RewriteBinaryOp(ast.NodeTransformer):
    # Rewrite binary operations in the AST
    def visit_BinOp(self, node):
        global visit_count, visit_target
        visit_count += 1
        if(visit_count == visit_target):
            ##print("Rewrite_binary Line: ", node.lineno)
            if(isinstance(node.op, ast.Add)):
                node.op = ast.Sub()
            elif(isinstance(node.op, ast.Sub)):
                node.op = ast.Add()
            elif(isinstance(node.op, ast.Mult)):
                node.op = ast.FloorDiv()
            elif(isinstance(node.op, ast.Div) or isinstance(node.op, ast.FloorDiv)):
                node.op = ast.Mult()

        return node

class RewriteFunctionCall(ast.NodeTransformer):
    # Rewrite function calls in the AST
    def visit_If(self, node):
        global if_found 
        if_found = 1
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        global visit_count, visit_target, if_found
        visit_count += 1
        if(if_found == 1):
            if_found = 0
            return node
        if(visit_count == visit_target):
            return ast.Pass()
        return node

    def visit_Assign(self, node):
        
        global visit_count, visit_target
        visit_count += 1
        if(visit_count == visit_target):
            return ast.copy_location(ast.Assign(targets=node.targets, value=ast.NameConstant(value=1)), node)
        return node
        
# Parse the target program
target_path = "./" + sys.argv[1]
number_of_mutants = int(sys.argv[2])
mutants_made = 0
tree = parse_target_program(target_path)

if_found = 0
assign_found = 0
number_of_comparisons = 0
number_of_binary = 0
number_of_assign = 0
number_of_call = 0
number_of_functioncall = 0

# Count comparisons, binary operations, function calls, and assignments in the AST
CountCompare().visit(tree)
CountBinaryOp().visit(tree)
CountFunctionCall().visit(tree)
number_of_functioncall = number_of_assign + number_of_call

mutant_combo_list = list()

visit_target = 0
visit_count = 0
seed = 0

# Create mutants until the required number is reached
while(mutants_made < number_of_mutants):
        random.seed(seed)
        seed += 1
        comparison_mutant = randint(1,number_of_comparisons)
        binary_mutant = randint(1,number_of_binary)
        functioncall_mutant = randint(1,number_of_functioncall)
        
        
        if([comparison_mutant, binary_mutant, functioncall_mutant] not in mutant_combo_list):
            mutant_combo_list.append([comparison_mutant, binary_mutant, functioncall_mutant])
            new_tree = copy.deepcopy(tree)
            visit_target = comparison_mutant
            visit_count = 0
            new_tree = RewriteCompare().visit(new_tree)
            visit_target = binary_mutant
            visit_count = 0
            new_tree = RewriteBinaryOp().visit(new_tree)
            visit_target = functioncall_mutant
            visit_count = 0
            if_found = 0
            new_tree = RewriteFunctionCall().visit(new_tree)
            # Create a new mutant file called 0.py, 1.py, .....
            file_name = str(mutants_made) + ".py"
            f = open(file_name, "w+")
            f.write(astor.to_source(new_tree))
            mutants_made += 1