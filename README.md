Project was under private repo, to which I moved it into a public repo, thus explaining 3 commits total.

# EOC-16 Virtual Machine & Assembler

A 16-bit virtual CPU and two-pass assembler, written in Python, that emulates a custom instruction set architecture (ISA) — including register storage, addressable memory, condition-code flags, and a full fetch-decode-execute cycle.

Independent project for CS220, under faculty guidance and in-class research.

## Features

Simulates a CPU with 8 general-purpose registers, 65,536 words of addressable memory, and N/Z/P condition-code flags.
Uses a two-pass assembler that translates `.asm` source into 16-bit machine code (`.eoc` binary files), with, symbol table resolution for labels (forward and backward references) and support for assembler directives: `.ORIG`, `.END`, `.FILL`, `.ASCII`, `.BLOCK`.
16 built-in instructions covering basic operations like arithmetic/logic, memory access, I/O, and control flow.
Command line shell for assembling, loading, running, and debugging programs.
Inspection tools for full understanding of machine state (dump memory pages, view register contents, and step through execution).

 ## Instruction Set

| Instruction | Description |

| `ADD` / `AND` | Arithmetic/logic, register or immediate (5-bit) operand mode |
| `NOT` | Bitwise complement |
| `LD` / `LDI` | Load direct / load indirect from memory |
| `ST` / `STI` | Store direct / store indirect to memory |
| `GET` / `GETC` | Read integer / character input into a register |
| `PUT` / `PUTC` | Write integer / character output from a register |
| `BR` | Conditional branch on N/Z/P flags |
| `JMP` / `JSR` / `RET` | Unconditional jump, subroutine call, and return |
| `HALT` | Stop execution |

Memory addressing uses a 9-bit page-relative offset scheme; `RUN` executes until a page boundary is crossed or `HALT` is reached.

## Usage

Run the simulator's command shell:

```bash
python3 eoc.py
```

## Available commands:

| Command | Description |

| `ASSEMBLE <in.asm> <out.eoc>` | Assemble a source file into machine code |
| `LOAD <file.eoc>` | Load a machine-code file into memory |
| `RUN` | Execute loaded program from the current instruction pointer |
| `DUMP` | Print the current memory page in binary |
| `REGISTERS` | Print all register contents |
| `STATE` | Print memory, registers, IP, IR, and condition flags |
| `CLEAR` | Reset memory, registers, and flags |

### Example session

```
Enter command: ASSEMBLE factorial.asm factorial.eoc
Assembled factorial.asm -> factorial.eoc (27 words)
Enter command: LOAD factorial.eoc
Enter command: RUN
Enter integer: 5
120
Enter command: STATE
---
---

## Assembly Language

Programs begin with an .ORIG directive specifying the start address in hexadecimal, and end with .END. Labels are defined by placing a name before an instruction and referenced directly in branch/jump operands:

```asm
.ORIG x3000
        GET   R1
LOOP    ADD   R0 R0 R1
        ADD   R1 R1 #-1
        BR    p LOOP
        PUT   R0
        HALT
.END
```

## File Structure


eoc.py          # CPU simulator, assembler, and command shell
*.asm           # Example assembly source programs
*.eoc           # Assembled machine-code output (16-bit binary, one instruction per line)


## Author

Jack Stecher — Coe College, BS Computer Science