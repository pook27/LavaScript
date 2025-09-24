import re
from compiler import Compiler

def parse(source_code):
    compiler = Compiler()
    # Strip comments and empty lines
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
            parse_assignment(var, expr, compiler)

        # While loop
        elif line.startswith("while"):
            m = re.match(r"while\s+(.+)\s+do", line)
            if not m:
                raise SyntaxError(f"Unsupported while syntax: {line}")

            condition_str = m.group(1).strip()

            # Extract lines until matching `end`
            body_lines, new_i = extract_block(lines, i)
            i = new_i

            # Recursive call for nested block
            def body():
                parse_lines(body_lines, compiler)

            compiler.compile_while(condition_str, body)

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
        if re.match(r"while\s+.*\s+do", line):
            depth += 1
        elif line == "end":
            depth -= 1
            if depth == 0:
                break
        body_lines.append(line)
        i += 1
    return body_lines, i
