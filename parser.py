import re
import sys
import traceback
import random
from compiler import Compiler

def parse(source_code, debug=True):
    compiler = Compiler()
    lines = [line.split("//")[0].strip() for line in source_code.split("\n")]
    lines = [line for line in lines if line]
    try:
        parse_lines(lines, compiler)
    except Exception as e:
        if debug:
            traceback.print_exc()
        error_type = type(e).__name__
        print(f"{error_type}: {e}", file=sys.stderr)
        sys.exit(1)
    return compiler.compile()

def parse_lines(lines, compiler):
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Assignment
        if re.match(r"^\w+\s*=\s*.+$", line):
            var, expr = [part.strip() for part in line.split("=")]
            if expr.startswith("'") and expr.endswith("'"):
                expr = str(ord(expr[1:-1]))
            parse_assignment(var, expr, compiler)

        # While loop
        elif line.startswith("while"):
            m = re.match(r"while\s*\(?(.+?)\)?\s*(\{)?$", line)
            if not m:
                raise SyntaxError(f"Unsupported while syntax: {line}")

            condition_str = m.group(1).strip()
            if not m.group(2):  # No '{' on same line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines) or lines[j].strip() != "{":
                    raise SyntaxError(f"Expected '{{' after while condition on line {i + 1}")
                i = j

            # Normalize special cases
            if condition_str == "True":
                condition_str = "0 == 0"
            elif condition_str == "False":
                condition_str = "0 != 0"
            elif condition_str == "Maybe":
                condition_str = f"0 != {random.randint(0, 1)}"
            body_lines, new_i = extract_block(lines, i, block_start="{", block_end="}")
            i = new_i
            def body():
                parse_lines(body_lines, compiler)
            compiler.compile_while(condition_str, body)

        # If conditional (with optional else)
        elif line.startswith("if"):
            m = re.match(r"if\s*\(?(.+?)\)?\s*(\{)?$", line)
            if not m:
                raise SyntaxError(f"Unsupported if syntax: {line}")
            condition_str = m.group(1).strip()
            if condition_str.startswith("(") and condition_str.endswith(")"):
                condition_str = condition_str[1:-1].strip()

            if not m.group(2):  # No '{' on same line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines) or lines[j].strip() != "{":
                    raise SyntaxError(f"Expected '{{' after if condition on line {i + 1}")
                i = j
            if condition_str == "True":
                condition_str = "0 == 0"
            elif condition_str == "False":
                condition_str = "0 != 0"
            elif condition_str == "Maybe":
                condition_str = f"0 != {random.randint(0, 1)}"

            body_lines, new_i = extract_block(lines, i, block_start="{", block_end="}")
            i = new_i

            # Check for optional else block
            has_else = False
            else_body_lines = []
            if i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith("else"):
                    has_else = True
                    m_else = re.match(r"else\s*(\{)?$", next_line)
                    if not m_else:
                        raise SyntaxError(f"Unsupported else syntax: {next_line}")
                    if not m_else.group(1):  # No '{' after else
                        j = i + 1
                        while j < len(lines) and not lines[j].strip():
                            j += 1
                        if j >= len(lines) or lines[j].strip() != "{":
                            raise SyntaxError(f"Expected '{{' after else on line {i + 1}")
                        i = j
                    else:
                        i = i  # '{' already present on same line
                    else_body_lines, new_i = extract_block(lines, i, block_start="{", block_end="}")
                    i = new_i
            def body():
                parse_lines(body_lines, compiler)
            if has_else:
                def else_body():
                    parse_lines(else_body_lines, compiler)
                compiler.compile_if_else(condition_str, body, else_body)
            else:
                compiler.compile_if(condition_str, body)

        # For loop
        elif line.startswith("for"):
            m = re.match(r"for\s*\(([^;]+);([^;]+);([^)]+)\)\s*(\{)?$", line)
            if not m:
                raise SyntaxError(f"Unsupported for-loop syntax: {line}")
            init_str = m.group(1).strip()
            condition_str = m.group(2).strip()
            increment_str = m.group(3).strip()

            if not m.group(4):  # No '{' on same line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines) or lines[j].strip() != "{":
                    raise SyntaxError(f"Expected '{{' after for loop header on line {i + 1}")
                i = j

            body_lines, new_i = extract_block(lines, i, block_start="{", block_end="}")
            i = new_i
            def body():
                parse_lines(body_lines, compiler)
            compiler.compile_for(init_str, condition_str, increment_str, body)

        elif line.startswith("print"):
            _, var = line.split("(",maxsplit = 1)
            var = var[:-1].strip()
            args = var.split(",")
            var = args[0].strip()
            special = args[1].strip() if len(args) > 1 else None
            if line.startswith("printc"):
                if var.startswith("'") and var.endswith("'"):
                    var= str(ord(var[1:-1]))
                compiler.compile_print(var, mode="PRINT_CHAR")
            elif line.startswith("println"):
                if var.startswith('"') and var.endswith('"'):
                    for chr in var[1:-1]:
                        compiler.compile_print(ord(chr), mode="PRINT_CHAR")
            else:
                compiler.compile_print(var, mode="PRINT")
            if special == "\\n":
                compiler.compile_print(10, mode="PRINT_CHAR")
        i += 1

def parse_assignment(var, expr, compiler):
    expr = expr.strip()
        # Tokenize the expression
    tokens = re.findall(r"\d+|\w+|[\+\-\*/\(\)]", expr)
    # Shunting Yard algorithm for precedence
    precedence = {'+': 1, '-': 1, '%': 1, '*': 2, '/': 2, '**':3}
    output = []
    ops = []
    for token in tokens:
        if re.match(r"^\d+$", token) or re.match(r"^\w+$", token):
            output.append(token)
        elif token in precedence:
            while (ops and ops[-1] in precedence and
                   precedence[ops[-1]] >= precedence[token]):
                output.append(ops.pop())
            ops.append(token)
        elif token == '(': 
            ops.append(token)
        elif token == ')':
            while ops and ops[-1] != '(': 
                output.append(ops.pop())
            ops.pop()  # Remove '('
    while ops:
        output.append(ops.pop())

    # Evaluate RPN and generate code
    stack = []
    temp_id = [0]
    def get_temp():
        temp_id[0] += 1
        return f"__tmp{temp_id[0]}"
    for token in output:
        if token in precedence:
            right = stack.pop()
            left = stack.pop()
            tmp = get_temp() if len(stack) > 0 or token != output[-1] else var
            lval = int(left) if left.isdigit() else left
            rval = int(right) if right.isdigit() else right
            compiler.compile_math(tmp, lval, token, rval)
            stack.append(tmp)
        else:
            stack.append(token)
    # Final assignment if needed
    if stack and stack[-1] != var:
        final = stack.pop()
        if final.isdigit():
            compiler.compile_assign(var, int(final))
        else:
            compiler.compile_assign(var, final)

def extract_block(lines, start_index, block_start="{", block_end="}"):
    body_lines = []
    depth = 1
    i = start_index + 1
    while i < len(lines) and depth > 0:
        line = lines[i]
        if line.strip() == block_start:
            depth += 1
        elif line.strip() == block_end:
            depth -= 1
            if depth == 0:
                break
        else:
            body_lines.append(line)
        i += 1
    return body_lines, i