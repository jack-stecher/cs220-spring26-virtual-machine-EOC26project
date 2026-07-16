class EOC:
    ip = 0 # next instruction to execute
    ir = 0 # current instruction being executed
    memory = []
    registers = []
    N = 0 # negative flag
    Z = 0 # zero flag
    P = 0 # positive flag

def clear(vc, params): # reset everything
    vc.memory = [0] * (2 ** 16)
    vc.registers = [0] * 8
    vc.ip = 0
    vc.ir = 0
    vc.N = 0
    vc.Z = 0
    vc.P = 0

def load(vc, params):
    parts = params.split() # split "fname" into list of tokens Ex. ["test.eoc"]
    fname = parts[0] # first token is the filename
    lines = [] # empty list to hold each line of binary from the file
    with open(fname, 'r') as f: # open program file
        for line in f:
            bits = line.strip()
            if bits: # skip blank lines
                lines.append(bits) # add binary string to lines list
    if not lines:
        print("Error: empty file.")
        return
    addr = int(lines[0], 2) # first line is the start address in binary, convert to integer
    vc.ip = addr # set instruction pointer to start address
    for i, bits in enumerate(lines[1:]): # loop through remaining
        vc.memory[addr + i] = int(bits, 2) # convert each binary string to integer and store in memory

def fmt(value):
    b = format(value & 0xFFFF, '016b') # shorten value to 16 bits then convert to 16-character binary string
    return ' '.join(b[i:i+4] for i in range(0, 16, 4)) # split into 16 bits into 4-bit chunks separated by spaces

def dump(vc, params):
    page_base = (vc.ip >> 9) << 9 # rights shift, left shift to reset ip
    for addr in range(page_base, page_base + 2**9): # loop through all 512 addresses on current page
        print(hex(addr), fmt(vc.memory[addr])) # print each address in hex and its contents

def registers(vc, params):
    for i in range(8): # loop through all 8 registers
        print("R" + str(i), fmt(vc.registers[i])) # print register name and its value

def state(vc, params):
    dump(vc, params)
    registers(vc, params)
    print("IP", fmt(vc.ip))
    print("IR", fmt(vc.ir))
    print("NZP", vc.N, vc.Z, vc.P)

def update_nzp(vc, value):
    vc.N = 1 if value < 0 else 0 # N if value is negative
    vc.Z = 1 if value == 0 else 0 # Z if value is zero
    vc.P = 1 if value > 0 else 0 # P if value is positive

def sign_extend(bits, width): # takes a binary string and its bit width
    value = int(bits, 2) # value gets bits and reads it as base 2 binary #, and so value gets unsigned integer
    if bits[0] == '1': # if bit at spot 0 is 1 v|v
        value -= (1 << width) # value gets 1 and shifts it left by width bits (2^width) giving us correct negative
    return value

def page_addr(vc, offset_bits):
    page_base = (vc.ip >> 9) << 9 # right shift ip 9 bits, then left shift ip 9 bits, to reset instruction pointer
    offset = int(offset_bits, 2) # offset gets offset_bits and reads it as base 2 binary #, and so offset gets unsigned integer
    return page_base + offset # returns offset page

def decode(bits):
    op = bits[0:4] # first 4 bits are the opcode
    if op == "0000": return "HALT"
    elif op == "0001": # ADD opcode
        dr = int(bits[4:7], 2); sr1 = int(bits[7:10], 2) # bits 4-6 = dr, bits 7-9 = sr1
        if bits[10] == "0": return "ADD R{} R{} R{}".format(dr, sr1, int(bits[13:16], 2)) # bit 10 = 0 means register mode, bits 13-15 = sr2
        else: return "ADD R{} R{} {}".format(dr, sr1, bits[11:16]) # bit 10 = 1 means immediate mode, bits 11-15 = imm5
    elif op == "0010": # AND opcode
        dr = int(bits[4:7], 2); sr1 = int(bits[7:10], 2) # bits 4-6 = dr, bits 7-9 = sr1
        if bits[10] == "0": return "AND R{} R{} R{}".format(dr, sr1, int(bits[13:16], 2)) # bit 10 = 0 means register mode
        else: return "AND R{} R{} {}".format(dr, sr1, bits[11:16]) # bit 10 = 1 means immediate mode
    elif op == "0011": return "NOT R{} R{}".format(int(bits[4:7], 2), int(bits[7:10], 2)) # NOT: bits 4-6 = dr, bits 7-9 = sr
    elif op == "0100": return "LD R{} {}".format(int(bits[4:7], 2), bits[7:16]) # LD: bits 4-6 = dr, bits 7-15 = offset9
    elif op == "0101": return "LDI R{} {}".format(int(bits[4:7], 2), bits[7:16]) # LDI: bits 4-6 = dr, bits 7-15 = offset9
    elif op == "0111": return "ST R{} {}".format(int(bits[4:7], 2), bits[7:16])  # ST: bits 4-6 = sr, bits 7-15 = offset9
    elif op == "1000": return "STI R{} {}".format(int(bits[4:7], 2), bits[7:16]) # STI: bits 4-6 = sr, bits 7-15 = offset9
    elif op == "1010":
        dr = int(bits[4:7], 2)
        return ("GET" if bits[7] == "0" else "GETC") + " R{}".format(dr) # bit 7 = 0 means int, bit 7 = 1 means character input
    elif op == "1011":
        sr = int(bits[4:7], 2)
        return ("PUT" if bits[7] == "0" else "PUTC") + " R{}".format(sr) # bit 7 = 0 means int output, bit 7 = 1 means character output
    elif op == "1100":             # BR opcode
        n, z, p = bits[4], bits[5], bits[6]    # bits 4, 5, 6 are the n, z, p condition flags
        status = ("n" if n=="1" else "") + ("z" if z=="1" else "") + ("p" if p=="1" else "")  # build flag string from whichever bits are set
        return "BR {} {}".format(status, bits[7:16]) # bits 7-15 = offset9
    elif op == "1101":
        return ("JSR" if bits[4] == "1" else "JMP") + " {}".format(bits[7:16]) # bit 4 = 1 means jsr, bit 4 = 0 means jmp, bits 7-15 = offset9
    elif op == "1111": return "RET"
    return "UNKNOWN"

def i_halt(vc, params): pass # just here to pass when HALT uses it from instruction_funcs, seperate if statement below that actually breaks the loop

def i_add(vc, params):
    parts = params.split(); dr = int(parts[0][1]); sr1 = int(parts[1][1]) # parts gets params.split() breaks the spaced data into separate strings in array, dr gets c0 r1, as integer, sr1 gets c1 r1, as integer
    a = vc.registers[sr1] # a gets sr1, integer
    if a >= 0x8000: a -= 0x10000 # if a >= 32768, turn it negative by a gets a - 65536
    if parts[2][0] == 'R': # checks first character of third string token in parts
        b = vc.registers[int(parts[2][1])] # if it's R, b gets register in third string that is converted to int
        if b >= 0x8000: b -= 0x10000 # same as a, checking if # needs to be turned negative
    else: b = sign_extend(parts[2], 5) # If parts[2][0] != R, b gets turned to signed bit integer
    result = a + b
    vc.registers[dr] = result & 0xFFFF # dr register gets result masked to 16 bits
    update_nzp(vc, result) # update nzp for future BR instructions that may be present

def i_and(vc, params):
    parts = params.split(); dr = int(parts[0][1]); sr1 = int(parts[1][1]) # parts gets params.split() breaks the spaced data into separate strings in array, dr gets c0 r1, as integer, sr1 gets c1 r1, as integer
    a = vc.registers[sr1] # a gets sr1, integer
    if parts[2][0] == 'R': # checks first character of third string token in parts
        b = vc.registers[int(parts[2][1])] # if it's R, b gets register in third string that is converted to int
    else: b = sign_extend(parts[2], 5) & 0xFFFF # If parts[2][0] != R, b gets turned to signed bit integer
    result = a & b # and the bits of a and b
    vc.registers[dr] = result & 0xFFFF  # dr register gets result & with 0xFFFF to keep result to 16 bits, Ex. result gets 65537 then output is 1
    update_nzp(vc, result if result < 0x8000 else result - 0x10000) # if result is positive, leave it, if result is > 32768, subtract 65536

def i_not(vc, params):
    parts = params.split(); dr = int(parts[0][1]); sr = int(parts[1][1]) # parts gets params.split() breaks the spaced data into separate strings in array, dr gets c0 r1, as integer, sr1 gets c1 r1, as integer
    result = (~vc.registers[sr]) & 0xFFFF # result gets sr register integer and nots them (-(x+1)) & with 0xFFFF to keep result to 16 bits
    vc.registers[dr] = result # dr gets result after ~ operation
    update_nzp(vc, result if result < 0x8000 else result - 0x10000) # if result is positive, leave it, if result is > 32768, subtract 65536

def i_ld(vc, params):
    parts = params.split(); dr = int(parts[0][1])  # parts gets params.split() breaks the spaced data into separate strings in array, dr gets c0 r1, as integer
    result = vc.memory[page_addr(vc, parts[1])] # calculate memory address from offset, result gets that value
    vc.registers[dr] = result # dr gets result
    update_nzp(vc, result if result < 0x8000 else result - 0x10000) # if result is positive, leave it, if result is > 32768, subtract 65536

def i_ldi(vc, params):
    parts = params.split(); dr = int(parts[0][1])  # parts gets params.split() breaks the spaced data into separate strings in array, dr gets c0 r1, as integer
    result = vc.memory[vc.memory[page_addr(vc, parts[1])]] # calculate memory address from offset, but this value is another address that points to another value and result gets that value
    vc.registers[dr] = result # dr gets result
    update_nzp(vc, result if result < 0x8000 else result - 0x10000) # if result is positive, leave it, if result is > 32768, subtract 65536

def i_st(vc, params):
    parts = params.split() # parts gets params.split() breaks the spaced data into separate strings in array
    vc.memory[page_addr(vc, parts[1])] = vc.registers[int(parts[0][1])] # calculate memory address from offset, store the value of sr register at that address

def i_sti(vc, params):
    parts = params.split() # parts gets params.split() breaks the spaced data into separate strings in array
    vc.memory[vc.memory[page_addr(vc, parts[1])]] = vc.registers[int(parts[0][1])] # calculate memory address from offset, that value is a pointer to another address, store sr register value at that second address

def i_get(vc, params):
    dr = int(params[1]); value = int(input("Enter integer: ")) # dr gets the register number from params, prompt user for an integer and store it in value
    vc.registers[dr] = value & 0xFFFF; update_nzp(vc, value) # store value in dr register masked to 16 bits, update NZP based on the value entered

def i_getc(vc, params):
    dr = int(params[1]); value = ord(input("Enter character: ")[0]) # dr gets the register number from params, prompt user for a character, ord() converts it to its ASCII integer value
    vc.registers[dr] = value & 0xFFFF; update_nzp(vc, value) # store ASCII value in dr register masked to 16 bits, update NZP based on the value

def i_put(vc, params):
    sr = int(params[1]); value = vc.registers[sr] # sr gets register number from params, value gets whatever is stored in that register
    if value >= 0x8000: value -= 0x10000 # if value >= 32768 it is a negative two's complement number, subtract 65536 to get correct signed value
    print(value) # print the integer value to screen

def i_putc(vc, params):
    print(chr(vc.registers[int(params[1])] & 0xFF)) # get register number from params, fetch its value masked to 8 bits, chr() converts the ASCII integer back to its character and prints it

def i_br(vc, params):
    parts = params.split(); flags = parts[0]; offset = int(parts[1], 2) # split params, flags gets the nzp string Ex. "nz", offset gets the 9-bit binary offset converted to integer
    branch = False # assume no branch until a matching flag is found
    if 'n' in flags and vc.N == 1: branch = True # if n flag set in instruction and machine N is 1, branch
    if 'z' in flags and vc.Z == 1: branch = True # if z flag set in instruction and machine Z is 1, branch
    if 'p' in flags and vc.P == 1: branch = True # if p flag set in instruction and machine P is 1, branch
    if branch: vc.ip = ((vc.ip >> 9) << 9) + offset # if a flag matched, set ip to page base + offset to jump to that instruction

def i_jmp(vc, params):
    vc.ip = ((vc.ip >> 9) << 9) + int(params.strip(), 2) # right shift ip 9 bits, then left shift ip 9 bits to reset it, then add the offset 9 value to jmp ip to that instruction

def i_jsr(vc, params):
    vc.registers[7] = vc.ip # store current ip in R7 so RET can return here after subroutine finishes
    vc.ip = ((vc.ip >> 9) << 9) + int(params.strip(), 2) # right shift ip 9 bits, then left shift ip 9 bits to reset it, then add the offset 9 value to jmp ip to that instruction

def i_ret(vc, params):
    vc.ip = vc.registers[7] # set ip to whatever was saved in R7 by JSR, returning execution to the instruction after jsr call

instruction_funcs = { # mapping decoded instruction name to its function
    "HALT": i_halt, "ADD": i_add,  "AND": i_and,  "NOT": i_not,
    "LD":   i_ld,   "LDI": i_ldi,  "ST":  i_st,   "STI": i_sti,
    "GET":  i_get,  "GETC":i_getc, "PUT": i_put,  "PUTC":i_putc,
    "BR":   i_br,   "JMP": i_jmp,  "JSR": i_jsr,  "RET": i_ret,
}

def run(vc, params):
    start_bit9 = (vc.ip >> 9) & 1 # record bit 9 of ip at start to detect page boundary crossing
    while True:
        if ((vc.ip >> 9) & 1) != start_bit9: break # if bit 9 of ip changes, we crossed a page boundary, stop
        vc.ir = vc.memory[vc.ip]; vc.ip += 1 # fetch instruction from memory at ip, then increment ip to point to next instruction
        bits = format(vc.ir & 0xFFFF, '016b') # convert fetched instruction integer to 16-bit binary string
        decoded = decode(bits) # decode binary string into human readable instruction e.g. "ADD R0 R1 R2"
        parts = decoded.split(maxsplit=1) # split decoded string into command and arguments
        cmd = parts[0] # first string is the instruction name Ex. "ADD"
        args = parts[1] if len(parts) > 1 else ""  # everything after the command is the arguments, empty string if no args
        if cmd in instruction_funcs: instruction_funcs[cmd](vc, args)  # look up and call the matching instruction function
        if cmd == "HALT": break # if instruction was HALT, stop the fetch loop


# ASSEMBLER

def blue_screen(vc, message): # blue screen of death
    print("ASSEMBLER ERROR: {}".format(message)) # state error
    state(vc, "") # state of machine
    clear(vc, "") # clear machine

def assemble_reg(token): # converts a register token Ex. "R3" into 3-bit binary string Ex. "011"
    if len(token) == 2 and token[0] == 'R' and token[1].isdigit(): # check token is exactly "R" followed by a digit
        r = int(token[1]) # get the register number
        if 0 <= r <= 7: # check if register is valid (0-7)
            return format(r, '03b') # return 3-bit binary string Ex. 3 -> "011"
    raise ValueError("Bad register: {}".format(token)) # bad register error

def assemble_imm5(token): # converts an immediate value string Ex. "#5" into 5-bit binary string Ex."00101"
    if token.startswith('#'): # if immediate values start with # v|v
        n = int(token[1:]) # get the integer after the # sign
        if n < -16 or n > 15: # check if imm5 imm5 < -16 or > 15 because these are only acceptable two's complements
            raise ValueError("imm5 out of range: {}".format(n))
        return format(n & 0x1F, '05b')  # adapt to 5 bits and return as binary string, & 0x1F handles negatives by keeping just last 5 bits
    raise ValueError("Bad imm5: {}".format(token))

def assemble_offset9(token, symbol_table=None, origin=0):
    if token.startswith('x') or token.startswith('X'): # if token is a hex address like x001B
        val = int(token[1:], 16) # convert hex string to integer Ex. x001B -> 27
        return format(val & 0x1FF, '09b') # keep only lower 9 bits, return as 9-bit binary string
    if symbol_table is not None and token in symbol_table: # if token is a label like LOOP
        abs_addr = symbol_table[token] # look up what address that label points to
        return format(abs_addr & 0x1FF, '09b') # keep only lower 9 bits, return as 9-bit binary string
    raise NameError("Undefined label: {}".format(token)) # token was neither a hex address nor a known label

def translate_instruction(opcode, operands, symbol_table=None, origin=0): # converts one assembly instruction into a 16-bit binary string
    op = opcode.upper()
    if op == "HALT":  return "0000000000000000" # HALT: all zeros
    elif op == "ADD":
        dr = assemble_reg(operands[0]); sr1 = assemble_reg(operands[1]) # get dr and sr1 as 3-bit strings
        if operands[2].startswith('#'): return "0001" + dr + sr1 + "1" + assemble_imm5(operands[2]) # immediate mode: bit 10 = 1
        else: return "0001" + dr + sr1 + "000" + assemble_reg(operands[2]) # register mode: bit 10 = 0, bits 11-12 = 00
    elif op == "AND":
        dr = assemble_reg(operands[0]); sr1 = assemble_reg(operands[1]) # get dr and sr1 as 3-bit strings
        if operands[2].startswith('#'): return "0010" + dr + sr1 + "1" + assemble_imm5(operands[2]) # immediate mode
        else: return "0010" + dr + sr1 + "000" + assemble_reg(operands[2]) # register mode
    elif op == "NOT":
        return "0011" + assemble_reg(operands[0]) + assemble_reg(operands[1]) + "111111" # NOT: dr, sr, then 6 ones for unused bits
    elif op == "LD":  return "0100" + assemble_reg(operands[0]) + assemble_offset9(operands[1], symbol_table, origin) # LD: opcode + dr + offset9
    elif op == "LDI": return "0101" + assemble_reg(operands[0]) + assemble_offset9(operands[1], symbol_table, origin) # LDI: opcode + dr + offset9
    elif op == "ST":  return "0111" + assemble_reg(operands[0]) + assemble_offset9(operands[1], symbol_table, origin) # ST: opcode + sr + offset9
    elif op == "STI": return "1000" + assemble_reg(operands[0]) + assemble_offset9(operands[1], symbol_table, origin) # STI: opcode + sr + offset9
    elif op == "GET":  return "1010" + assemble_reg(operands[0]) + "011111111" # GET: bit 7 = 0 for integer, remaining bits filled with 1s
    elif op == "GETC": return "1010" + assemble_reg(operands[0]) + "111111111" # GETC: bit 7 = 1 for character
    elif op == "PUT":  return "1011" + assemble_reg(operands[0]) + "011111111" # PUT: bit 7 = 0 for integer
    elif op == "PUTC": return "1011" + assemble_reg(operands[0]) + "111111111" # PUTC: bit 7 = 1 for character
    elif op == "BR":
        flags = operands[0].lower() # get flag string e.g. "nzp"
        n = "1" if "n" in flags else "0" # bit 4: 1 if n flag present
        z = "1" if "z" in flags else "0" # bit 5: 1 if z flag present
        p = "1" if "p" in flags else "0" # bit 6: 1 if p flag present
        return "1100" + n + z + p + assemble_offset9(operands[1], symbol_table, origin) # BR: opcode + nzp bits + offset9
    elif op == "JMP": return "1101000" + assemble_offset9(operands[0], symbol_table, origin) # JMP: opcode + L=0 + 00 + offset9
    elif op == "JSR": return "1101100" + assemble_offset9(operands[0], symbol_table, origin) # JSR: opcode + L=1 + 00 + offset9
    elif op == "RET": return "1111000000000000" # RET: opcode 1111 followed by zeros
    raise ValueError("Unknown opcode: {}".format(op)) # opcode not recognised, raise error

DIRECTIVES = {".ORIG", ".END", ".FILL", ".ASCII", ".BLOCK"} # set of all assembler directives

KEYWORDS = { # set of all reserved words — used to detect labels vs opcodes
    "ADD", "AND", "NOT", "LD", "LDI", "ST", "STI",
    "GET", "GETC", "PUT", "PUTC", "BR", "JMP", "JSR", "RET", "HALT"
} | DIRECTIVES # union with directives so labels are never mistaken for either

def get_source_lines(raw_lines): # strips comments and blank lines from raw file content
    source = []
    for raw in raw_lines:
        stripped = raw.strip() # remove leading/trailing whitespace
        if not stripped or stripped.startswith(';'): continue # skip blank lines and full-line comments
        if ';' in stripped: stripped = stripped[:stripped.index(';')].strip() # remove inline comments
        if stripped: source.append(stripped) # add cleaned line to source
    return source

def build_symbol_table(source_lines): # Pass 1: scan all lines and record label -> address in symbol table
    symbol_table = {} # dictionary mapping label names to their memory addresses
    origin = None # start address, set by .ORIG directive
    addr = 0 # tracks current address as we walk through the program

    for line in source_lines:
        tokens = line.split() # creates tokens from source_lines Ex. ADD R1 R2 #5 -> ["ADD", "R1", "R2", "#5"]

        if tokens[0].upper() not in KEYWORDS: # if first token is not a keyword, it must be a label
            label = tokens[0]
            symbol_table[label] = addr # record label and the address it points to
            tokens = tokens[1:] # skip past label to get opcode

        if not tokens:
            continue

        op = tokens[0].upper()

        if op == ".ORIG":
            origin = int(tokens[1][1:], 16) # convert hex address to decimal Ex. .ORIG x3000 -> 12288
            addr = origin # what  start storing at origin address

        elif op == ".END":
            break # stop reading the file

        elif op == ".ASCII":
            string = tokens[1]
            addr += len(string) + 1 # reserve space for characters and null terminator, Ex. .ASCII "CAT" 1 add for C, 1 forA, 1 for T, and 1 for null (0), in turn addr increases by 4

        elif op == ".BLOCK":
            addr += int(tokens[1]) # reserve block of addresses by moving addr a specified amount Ex. .BLOCK 5

        else:
            addr += 1 # every normal instruction/directive takes one address

    if origin is None:
        raise ValueError("Missing .ORIG directive") # every program needs .ORIG

    return symbol_table, origin

def assemble(vc, params):
    parts = params.split()
    if len(parts) < 2:
        print("Usage: ASSEMBLE <input.asm> <output.eoc>")
        return
    in_fname = parts[0]; out_fname = parts[1] # input asm file and output eoc file
    try:
        with open(in_fname, 'r') as f:
            raw_lines = f.readlines() # read all lines from asm file
    except FileNotFoundError:
        print("File not found: {}".format(in_fname)); return

    source_lines = get_source_lines(raw_lines) # remove comments and blank lines

    try:
        symbol_table, origin = build_symbol_table(source_lines) # Pass 1: build label -> address table
    except Exception as e:
        blue_screen(vc, "Symbol table error: {}".format(e)); return

    output_lines = [format(origin, '016b')] # first output line is start address in binary

    try:
        for line in source_lines: # Pass 2: translate source lines into binary
            tokens = line.split()
            if tokens[0].upper() not in KEYWORDS:
                tokens = tokens[1:] # skip label if line has one
            if not tokens:
                continue
            opcode = tokens[0].upper()
            operands = tokens = tokens[1:] # everything after opcode is operands

            if opcode == ".ORIG":
                origin = int(operands[0][1:], 16) # update origin from .ORIG
                output_lines = [format(origin, '016b')] # reset output with new start address
                continue
            elif opcode == ".END":
                output_lines.append("0000000000000000") # write null terminator word
                break # stop translating

            elif opcode == ".SET":
                value = int(operands[0])
                output_lines.append(format(value & 0xFFFF, '016b')) # store integer as 16-bit binary

            elif opcode == ".FILL":
                value = int(operands[0][1:], 16) # convert hex value Ex. xFFDF
                output_lines.append(format(value & 0xFFFF, '016b')) # store as 16-bit binary

            elif opcode == ".ASCII":
                string = operands[0]
                for ch in string:
                    output_lines.append(format(ord(ch) & 0xFFFF, '016b')) # store one character per word
                output_lines.append("0000000000000000") # add null terminator

            elif opcode == ".BLOCK":
                count = int(operands[0])
                for _ in range(count):
                    output_lines.append("0000000000000000") # reserve memory with null words

            else:
                output_lines.append( # translate instruction into binary
                    translate_instruction(opcode, operands, symbol_table, origin)
                )
    except NameError as e:
        blue_screen(vc, str(e)); return # undefined label error
    except ValueError as e:
        blue_screen(vc, str(e)); return # invalid opcode/register/immediate error

    for bits in output_lines: # verify every output line is valid binary
        if len(bits) != 16 or not all(c in '01' for c in bits):
            blue_screen(vc, "Bad output line: {}".format(bits)); return # invalid binary line detected

    with open(out_fname, 'w') as f:
        for bits in output_lines:
            f.write(bits + "\n") # write each binary line to output file
    print("Assembled {} -> {} ({} words)".format(in_fname, out_fname, len(output_lines) - 1))

def main():
    vc = EOC() # create a vc
    commands = { # mapping cmd strings to their functions
        "CLEAR": clear, "LOAD": load, "DUMP": dump,
        "REGISTERS": registers, "STATE": state,
        "RUN": run, "ASSEMBLE": assemble,
    }
    clear(vc, "") # clear machine immidiately when ran
    while True:
        raw = input("Enter command: ").strip() # prompt for cmd
        if not raw: continue # ignore blank input
        parts = raw.split(maxsplit=1) # split into command and params Ex. "LOAD test.eoc" -> ["LOAD", "test.eoc"]
        cmd = parts[0].upper() # set cmd name to uppercase
        params = parts[1] if len(parts) > 1 else "" # everything after the command, empty string if none
        if cmd in commands: commands[cmd](vc, params) # look up and call the matching command function

if __name__ == "__main__":
    main()