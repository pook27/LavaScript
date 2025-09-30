symbols = {
    "SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4,
    "R0":0, "R1":1, "R2":2, "R3":3, "R4":4,
    "R5":5, "R6":6, "R7":7, "R8":8, "R9":9,
    "R10":10, "R11":11, "R12":12, "R13":13, "R14":14, "R15":15,
    "SCREEN":16384, "KBD":24576
}

print_table = {
    "PRINT":"01", "PRINT_CHAR":"10", "NO_PRINT":"11"
}

# C-instruction tables
comp_table = {
    "0":"0101010", "1":"0111111", "-1":"0111010",
    "D":"0001100", "A":"0110000", "M":"1110000",
    "!D":"0001101", "!A":"0110001", "!M":"1110001",
    "-D":"0001111", "-A":"0110011", "-M":"1110011",
    "D+1":"0011111", "A+1":"0110111", "M+1":"1110111",
    "D-1":"0001110", "A-1":"0110010", "M-1":"1110010",
    "D+A":"0000010", "D+M":"1000010", "D-A":"0010011", "D-M":"1010011",
    "A-D":"0000111", "M-D":"1000111", "D&A":"0000000", "D&M":"1000000",
    "D|A":"0010101", "D|M":"1010101"
}

dest_table = {
    None:"000", "M":"001", "D":"010", "MD":"011", "A":"100", "AM":"101", "AD":"110", "AMD":"111"
}

jump_table = {
    None:"000", "JGT":"001", "JEQ":"010", "JGE":"011",
    "JLT":"100", "JNE":"101", "JLE":"110", "JMP":"111"
}

def assemble(asm_code):
    lines = [line.split("//")[0].strip() for line in asm_code.split("\n")]
    lines = [line for line in lines if not line.startswith("//")]
    lines = [line for line in lines if line.strip() != ""]

    #1st pass: get all the labels
    rom_address = 0
    labels = {}
    for line in lines:
        if line.startswith("(") and line.endswith(")"):
            labels[line[1:-1]] = rom_address
        else:
            rom_address += 1

    #2nd pass: instructions
    nvar = 1
    output = []

    for line in lines:
        if line.startswith("("):
            continue

        if line.startswith("@"):
            symbol = line[1:]

            if symbol.isdigit():
                addr = int(symbol)
            elif symbol in labels:
                addr = labels[symbol]
            elif symbol in symbols:
                addr = symbols[symbol]
            else:
                symbols[symbol] = nvar
                addr = nvar
                nvar += 1
            output.append(f"0{addr:015b}")
        else:
            if line.startswith("PRINT") or line.startswith("PRINT_CHAR"):
                prnt, expr = line.split(" ", maxsplit=1)
                prnt  =prnt.strip()
                expr = expr.strip()
            else:
                prnt = "NO_PRINT"
                expr = line
            if "=" in expr:
                dest, comp_jump = line.split("=")
                dest = dest.strip()
            else:
                dest = None
                comp_jump = expr
            if ";" in comp_jump:
                comp, jump = comp_jump.split(";")
                comp = comp.strip()
                jump = jump.strip()
            else:
                comp = comp_jump.strip()
                jump = None

            print_bits = print_table[prnt]
            comp_bits = comp_table[comp]
            dest_bits = dest_table[dest]
            jump_bits = jump_table[jump]
            code = f"1{print_bits}{comp_bits}{dest_bits}{jump_bits}"
            output.append(code)
    return output

if __name__ == "__main__":
    with open("prog.asm") as f:
        asm_code = f.read()
    output = assemble(asm_code)
    print(output)