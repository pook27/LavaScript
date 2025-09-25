import sys
from cpu import CPU
from parser import parse

input_file = sys.argv[1]

with open(input_file) as f:
    if input_file.endswith(".ls"):
        source = f.read()
    else:
        raise ValueError("Input file is not a .ls file")

program , vars = parse(source)

if __name__ =="__main__":
    cpu = CPU(program)
    cpu.run(vars)
