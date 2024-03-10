import sys, ast, astor, random, pprint

class myVisitor(ast.NodeVisitor):
    def __init__(self):
        # Initialize counter to keep track of nodes visited
        self.counter = 0

    def visit_Assign(self, node):
        # Increment counter and print message when visiting assignment nodes
        if isinstance(node, ast.Assign):
            self.counter += 1
            print('Visiting Assign node, counter = {}'.format(self.counter))
        # Continue traversal to other nodes
        return self.generic_visit(node)

    def visit_BinOp(self, node):
        # Increment counter and print message for binary operation nodes based on the operation type
        if isinstance(node.op, ast.Add):
            self.counter += 1
            print('Visiting Add operation, counter = {}'.format(self.counter))
        if isinstance(node.op, ast.Sub):
            self.counter += 1
            print('Visiting Sub operation, counter = {}'.format(self.counter))
        if isinstance(node.op, ast.Mult):
            self.counter += 1
            print('Visiting Mult operation, counter = {}'.format(self.counter))
        if isinstance(node.op, ast.FloorDiv):
            self.counter += 1
            print('Visiting FloorDiv operation, counter = {}'.format(self.counter))
        if isinstance(node.op, ast.Div):
            self.counter += 1
            print('Visiting Div operation, counter = {}'.format(self.counter))
        # Continue traversal to other nodes
        return self.generic_visit(node)

    def visit_Compare(self, node):
        # Increment counter and print message when visiting comparison nodes based on the comparison type
        if any(isinstance(op, ast.GtE) for op in node.ops):
            self.counter += 1
            print('Visiting GtE comparison, counter = {}'.format(self.counter))
        if any(isinstance(op, ast.Gt) for op in node.ops):
            self.counter += 1
            print('Visiting Gt comparison, counter = {}'.format(self.counter))
        if any(isinstance(op, ast.LtE) for op in node.ops):
            self.counter += 1
            print('Visiting LtE comparison, counter = {}'.format(self.counter))
        if any(isinstance(op, ast.Lt) for op in node.ops):
            self.counter += 1
            print('Visiting Lt comparison, counter = {}'.format(self.counter))
        # Continue traversal to other nodes
        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        # Increment counter and print message when visiting boolean operations based on the operation type
        if isinstance(node.op, ast.And):
            self.counter += 1
            print('Visiting And operation, counter = {}'.format(self.counter))
        # Continue traversal to other nodes
        return self.generic_visit(node)

class myTransformer(ast.NodeTransformer):
    def __init__(self, nodeToMutate):
        # Initialize with the target node to mutate
        self.counter = 0
        self.nodeToMutate = nodeToMutate

    def visit_BinOp(self, node):
        # Transform the operation of binary operator nodes when the counter matches the target node
        self.counter += 1
        if self.counter == self.nodeToMutate:
            # Change the operation based on the current operation
            if isinstance(node.op, ast.Add):
                print('Changing Add to Sub for node {}'.format(self.counter))
                node.op = ast.Sub()
            elif isinstance(node.op, ast.Sub):
                print('Changing Sub to Add for node {}'.format(self.counter))
                node.op = ast.Add()
            elif isinstance(node.op, ast.FloorDiv):
                print('Changing FloorDiv to Div for node {}'.format(self.counter))
                node.op = ast.Div()
            elif isinstance(node.op, ast.Div):
                print('Changing Div to FloorDiv for node {}'.format(self.counter))
                node.op = ast.FloorDiv()
            elif isinstance(node.op, ast.Mult):
                print('Changing Mult to Pow for node {}'.format(self.counter))
                node.op = ast.Pow()
            return node
        return self.generic_visit(node)

    def visit_Compare(self, node):
        # Transform the comparison operator of comparison nodes when the counter matches the target node
        self.counter += 1
        if self.counter == self.nodeToMutate:
            # Change the comparison operator based on the current operator
            if any(isinstance(op, ast.LtE) for op in node.ops):
                print('Changing LtE to Gt for node {}'.format(self.counter))
                node.ops = [ast.Gt()]
            elif any(isinstance(op, ast.GtE) for op in node.ops):
                print('Changing GtE to Lt for node {}'.format(self.counter))
                node.ops = [ast.Lt()]
            # Additional comparisons can be added here following the same pattern
            return node
        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        # Transform the boolean operation when the counter matches the target node
        self.counter += 1
        if self.counter == self.nodeToMutate:
            # Change the boolean operation based on the current operation
            if isinstance(node.op, ast.And):
                print('Changing And to Or for node {}'.format(self.counter))
                node.op = ast.Or()
            elif isinstance(node.op, ast.Or):
                print('Changing Or to And for node {}'.format(self.counter))
                node.op = ast.And()
            return node
        return self.generic_visit(node)

    def visit_Assign(self, node):
        # Delete the assignment node when the counter matches the target node
        self.counter += 1
        if self.counter == self.nodeToMutate:
            print('Deleting assignment for node {}'.format(self.counter))
            return None  # Remove the node by returning None
        return self.generic_visit(node)

# Parse the source code from a file provided in the command line arguments
my_tree = None
with open(sys.argv[1]) as f:
    source = f.read()
    my_tree = ast.parse(source)

# Perform mutations based on the second command line argument
for i in range(int(sys.argv[2])):
    my_visited_tree = myVisitor()
    my_visited_tree.visit(my_tree)

    node_to_mutate = random.randint(1, my_visited_tree.counter)
    my_transformed_node = myTransformer(node_to_mutate)
    my_transformed_node.visit(my_tree)

# Output the mutated source code
print(astor.to_source(my_tree))