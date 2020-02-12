import sys, ast

def printAst(ast, indent='  ', stream=sys.stdout, initlevel=0):
    "Pretty-print an AST to the given output stream."
    print_node(ast, initlevel, indent, stream.write)
    stream.write('\n')

def print_node(node, level, indent, write):
    "Recurse through a node, pretty-printing it."
    pfx = indent * level
    pfx_prev = indent * (level - 1)
    if not isinstance(node, list):
        write(node.__class__.__name__)
    if hasattr(node, 'body'):
        if hasattr(node, 'name'):
            write(" '" + node.name + "' ")
        write('(\n')
        for child in node.body:
            write(pfx)
            print_node(child, level+1, indent, write)
            write('\n')
        write(pfx_prev + ')')
    elif hasattr(node, 'value'):
        write('[ ')
        if hasattr(node, 'targets'):
            print_node(node.targets, level+1, indent, write)
            write(' = ')
        print_node(node.value, level+1, indent, write)
        if hasattr(node, 'attr'):
            write('.')
            write(node.attr)
        write(' ]')
    elif hasattr(node, 'func'):
        write('(')
        print_node(node.func, level+1, indent, write)
        if hasattr(node, 'args'):
            write('(')
            print_node(node.args, level+1, indent, write)
            write(')')
        write(')')
    elif isinstance(node, list):
        for n in node:
            print_node(n, level+1, indent, write)
            write(',')
    elif hasattr(node, 'id'):
        write('(' + repr(node.id) + ')')
    elif hasattr(node, 's'):
        write('(' + repr(node.s) + ')')


def main():
    if len(sys.argv) < 2:
        parser.error("You need to specify the name of Python files to print out.")

    import traceback
    for fn in sys.argv[1:]:
        print('\n\n%s:\n' % fn)
        try:
            f = open(fn, 'r')
            source = f.read()
            printAst(ast.parse(source), initlevel=1)
        except SyntaxError:
            traceback.print_exc()

if __name__ == '__main__':
    main()