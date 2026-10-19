# LavaScript Project Review

Oct 19, 2026 · @thicckque

## Overview

The two most urgent problems in LavaScript are that nested blocks don't compile and that the 13th variable overwrites a scratch register. LavaScript is a toy language that compiles `.ls` files to Hack assembly and runs them on a Python CPU emulator.

I cloned `pook27/lavascript` (six Python files, about 870 lines), read all of it, and ran small probe programs to confirm each problem below. I changed nothing in the repository.

## Bugs confirmed by running them

Seven problems reproduced on real programs; the first three produce wrong or broken output on very ordinary code.

| # | Problem | What happens | Fix direction |
| --- | --- | --- | --- |
| 1 | Nested blocks | An `if` inside a `while` fails in both brace styles. With `{` on its own line: `SyntaxError: Expected '{'`, because `extract_block` discards the inner brace lines. With `{` on the same line, the first inner `}` ends the outer block early; in my test `i = i + 1` fell outside the loop and the program hung. | Count braces properly; best solved by an AST parser |
| 2 | Variables collide with scratch registers | Variables are allocated from RAM address 1, but `*` and `/` use R13–R15 (addresses 13–15). The 13th variable, counting compiler temporaries, gets overwritten: `a13 = 13` printed `0` once a later line multiplied. | Start variables at 16, the Hack convention |
| 3 | Silent wrong operators | `7 % 3` prints `3` and `6 & 3` prints `3`. The tokenizer drops `%`, `&`, `\|` and `**`, so only the last operand survives. The README advertises `&` and `\|`. | Tokenize and implement them, or raise an error |
| 4 | `or` acts like `and` | `x = 5; if x == 1 or x == 5` takes the else branch. Conditions are split on the raw substrings "or" and "and", so a variable named `color` fails with `Unsupported condition: col`. | Tokenize conditions; emit real short-circuit jumps |
| 5 | `Maybe` is fixed at compile time | It is not random per iteration. In 8 runs of `while Maybe`, 7 exited immediately and 1 looped forever. | Add a runtime random opcode in the CPU |
| 6 | Hangs and crashes | Division by zero loops forever. Multiplying by a negative number also loops forever. Unary minus (`x = -5`) crashes with `IndexError`. | Guard divide and multiply; support unary minus |
| 7 | Silent ignores | A typo like `prnt(x)` or a bare `x++` does nothing. Reading an undefined variable gives `0`. `println("Hello, world")` prints nothing because the argument is split on the comma. | Error on unknown statements and undefined variables; parse strings properly |

## Structural improvements

Replacing the regex parser would fix most of the bugs above at once; the other changes are smaller.

- **Replace the line-by-line regex parser.** A tokenizer plus a recursive-descent parser that builds an AST, with a separate code generator, fixes nesting, `and`/`or`, operator precedence and unary minus together. It also allows errors with line numbers instead of Python tracebacks.
- **Speed up the CPU.** It stores 64-bit words as strings of `'0'` and `'1'`, and the ALU converts them on every operation. A 100,000-iteration loop took about 16 seconds. Plain ints in the emulator would be much faster; `alu.py` can stay as the bit-level teaching version.
- **Clean up `melt`.** It reads the file at import time, crashes without arguments, and hard-codes `debug=True` and `diagnostics=False`. `argparse` flags such as `--asm` (dump assembly) and `--diagnostics` would help.
- **Remove the assembler's shared state.** It mutates a module-level `symbols` dict between calls, which will cause trouble once tests exist.

## Repo hygiene

The repository currently blocks its own example programs, tracks generated files, and has no tests.

- **`.gitignore` contains `*.ls`**, so no LavaScript program can be committed. That is why `examples/example.ls` from the README doesn't exist.
- **Generated files are tracked.** `__pycache__/` and `.idea/` (12 files) are committed, with no ignore rule for them.
- **No tests or CI.** A small pytest suite of `.ls` programs with expected output would have caught most of the bugs above.
- **The README needs repair.** A code fence swallows the "to compile and execute" sentence, the Roadmap and License markdown is broken, and `else`, `println` and `, "\n"` are undocumented.
- **No license file.** The README says "do whatever you want"; MIT, Unlicense or CC0 would make that explicit.
- **`parser.py` shares its name with a removed stdlib module.** Something like `lava_parser.py` is clearer.

## Language features and next steps

Once the bugs are fixed, the roadmap items (functions, strings and arrays, `%`) are the natural next features. Beyond those, I would add `else if`, `break` and `continue`, `+=`, expressions inside conditions, and an error for undefined variables.

Suggested order of work:

1. Add `__pycache__/` and `.idea/` to `.gitignore`, remove `*.ls` from it, and add example programs.
2. Move variable allocation to start at address 16.
3. Write the tokenizer and AST parser, which fixes nesting, `and`/`or`, unary minus and the silent operator drops.
4. Add pytest tests and CI, then speed up the CPU.
