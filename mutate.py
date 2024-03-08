import sys
import ast
import astor

class Mutator(ast.NodeTransformer):
    def __init__(self):
        self.op_map = {ast.LtE: ast.Gt,
                    ast.GtE: ast.Lt,
                    ast.Lt: ast.GtE,
                    ast.Gt: ast.LtE,
                    ast.Add: ast.Sub,
                    ast.Sub: ast.Add,
                    ast.Mult: ast.FloorDiv,
                    ast.FloorDiv: ast.Mult
                    }
        
    def visit_BinOp(self, node):
        old_node = node
        new_op = self.op_map.get(type(node.op))
        print(old_node.op, node.lineno)
        if new_op in self.op_map:
            new_op_node = new_op()
            ast.copy_location(new_op_node, node.op)
            ast.fix_missing_locations(new_op_node)
            node.op = new_op_node
        print(f"now: {type(node.op)}")
        return old_node

    #this makes the unparsing throw error, need fix
    def visit_Compare(self, node):
        print(node.ops, node.lineno)
        #expect a list for node.ops

        new_ops = []

        for comparator in node.ops:
            old_op_type = type(comparator)
            new_op_class = self.op_map.get(old_op_type)

            if new_op_class:
                new_op = new_op_class()
                ast.copy_location(new_op, comparator)
                ast.fix_missing_locations(new_op)
                print(f"Changed {old_op_type} to {type(new_op)}")
                new_ops.append(new_op)
            else:
                new_ops.append(comparator)

            print(f"old ops: {node.ops}. new ops: {new_ops}")

        # Replace the ops attribute with the modified list
        node.ops = new_ops


def main():
    if len(sys.argv) != 3:
        print("Usage: python mutate.py <source_program> <num_mutants>")
        return

    source_program = sys.argv[1]
    num_mutants = int(sys.argv[2])

    with open(source_program, "r") as source:
        # print(ast.dump(ast.parse(source.read()), indent=2))
        tree = ast.parse(source.read())

    mutator = Mutator()
    changed = mutator.visit(tree)

    # changed_src = astor.to_source(changed)
    changed_src = ast.unparse(changed)
    mutated_file_path = source_program.replace('.py', '_mutated.py')
    with open(mutated_file_path, 'w') as mutated_file:
        mutated_file.write(changed_src)

if __name__ == "__main__":
    main()
