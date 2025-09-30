import re
from compiler import Compiler

def parse(source_code):
    compiler = Compiler()
    lines = [line.split("//")[0].strip() for line in source_code.split("\n")]
    lines = [line for line in lines if line]
    parse_lines(lines, compiler)
    return compiler.compile()

def parse_lines(lines, compiler):
    i = 0
    while i < len(lines):
        line = lines[i]

        # Assignment
        if re.match(r"^\w+\s*=\s*.+$", line):
            var, expr = [part.strip() for part in line.split("=")]
            if expr.startswith("'") and expr.endswith("'"):
                expr = str(ord(expr[1:-1]))
            parse_assignment(var, expr, compiler)

        # While loop
        elif line.startswith("while"):
            m = re.match(r"while\s+(.+)\s+do", line)
            if not m:
                raise SyntaxError(f"Unsupported while syntax: {line}")

            condition_str = m.group(1).strip()
            body_lines, new_i = extract_block(lines, i)
            i = new_i
            # Recursive call for nested block
            def body():
                parse_lines(body_lines, compiler)

            compiler.compile_while(condition_str, body)

        # If conditional
        elif line.startswith("if"):
            m = re.match(r"if\s+(.+)\s+then", line)
            if not m:
                raise SyntaxError(f"Unsupported if syntax: {line}")
            condition_str = m.group(1).strip()
            body_lines, new_i = extract_block(lines, i)
            i = new_i
            # Recursive call for nested block
            def body():
                parse_lines(body_lines, compiler)

            compiler.compile_if(condition_str, body)

        elif line.startswith("for"):
        # Syntax: for (init; condition; increment) do
            m = re.match(r"for\s*\(([^;]+);([^;]+);([^\)]+)\)\s*do", line)
            if not m:
                raise SyntaxError(f"Unsupported for-loop syntax: {line}")
            init_str = m.group(1).strip()
            condition_str = m.group(2).strip()
            increment_str = m.group(3).strip()
            body_lines, new_i = extract_block(lines, i)
            i = new_i
            def body():
                parse_lines(body_lines, compiler)
            compiler.compile_for(init_str, condition_str, increment_str, body)

        elif line.startswith("print"):
            _, var = line.split(maxsplit = 1)
            if line.startswith("printc"):
                if var.startswith("'") and var.endswith("'"):
                    var= str(ord(var[1:-1]))
                compiler.compile_print(var, mode="PRINT_CHAR")
            else:
                compiler.compile_print(var, mode="PRINT")
        i += 1

def parse_assignment(var, expr, compiler):
    expr = expr.strip()
    m = re.match(r"^(\w+|\d+)\s*([\+\-\*/])\s*(\w+|\d+)$", expr)
    if m:
        left, op, right = m.groups()
        left = int(left) if left.isdigit() else left
        right = int(right) if right.isdigit() else right
        compiler.compile_math(var, left, op, right)
        return
    if expr.isdigit():
        compiler.compile_assign(var, int(expr))
    else:
        compiler.compile_assign(var, expr)

def extract_block(lines, start_index):
    body_lines = []
    depth = 1
    i = start_index + 1
    while i < len(lines) and depth > 0:
        line = lines[i]
        if re.match(r"while\s+.*\s+do", line) or re.match(r"if\s+.*\s+then", line):
            depth += 1
        elif line == "end":
            depth -= 1
            if depth == 0:
                break
        body_lines.append(line)
        i += 1
    return body_lines, i
