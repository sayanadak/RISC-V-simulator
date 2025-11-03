from ram import read, write, ram

def load_bin_file_to_ram(filepath, start_addr=0x80000000):
    """Load a binary file into simulated RAM."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        for i, byte in enumerate(data):
            write(start_addr + i, byte)
        print(f"Loaded {len(data)} bytes from '{filepath}' at {hex(start_addr)}")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        exit(1)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def get_word(addr):
    """Read a 32-bit word from RAM (little-endian)."""
    return (read(addr) |
           (read(addr+1) << 8) |
           (read(addr+2) << 16) |
           (read(addr+3) << 24))


def sign_extend(value, bits):
    """Sign-extend a number of given bit width to Python int."""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def decode(inst):
    """Decode a 32-bit RISC-V instruction into assembly string."""
    opcode = inst & 0x7f
    rd     = (inst >> 7) & 0x1f
    funct3 = (inst >> 12) & 0x7
    rs1    = (inst >> 15) & 0x1f
    rs2    = (inst >> 20) & 0x1f
    funct7 = (inst >> 25) & 0x7f

    # --- Lookup tables ---
    rtype = {
        (0x0,0x00): "add", (0x0,0x20): "sub", (0x1,0x00): "sll",
        (0x2,0x00): "slt", (0x3,0x00): "sltu",(0x4,0x00): "xor",
        (0x5,0x00): "srl", (0x5,0x20): "sra", (0x6,0x00): "or",
        (0x7,0x00): "and",
    }
    muldiv = {
        0x0:"mul", 0x1:"mulh", 0x2:"mulhsu", 0x3:"mulhu",
        0x4:"div", 0x5:"divu", 0x6:"rem",    0x7:"remu"
    }
    itype = {0x0:"addi",0x2:"slti",0x3:"sltiu",0x4:"xori",0x6:"ori",0x7:"andi"}
    ishift = {(0x1,0x00):"slli",(0x5,0x00):"srli",(0x5,0x20):"srai"}
    loads = {0x0:"lb",0x1:"lh",0x2:"lw",0x4:"lbu",0x5:"lhu"}
    stores= {0x0:"sb",0x1:"sh",0x2:"sw"}
    branches={0x0:"beq",0x1:"bne",0x4:"blt",0x5:"bge",0x6:"bltu",0x7:"bgeu"}

    # --- Decode by opcode ---
    if opcode == 0b0110011:  # R-type
        if funct7 == 0x01 and funct3 in muldiv:
            return f"{muldiv[funct3]} x{rd}, x{rs1}, x{rs2}"
        if (funct3,funct7) in rtype:
            return f"{rtype[(funct3,funct7)]} x{rd}, x{rs1}, x{rs2}"

    elif opcode == 0b0010011:  # I-type ALU
        imm, shamt, funct7i = sign_extend(inst>>20,12), (inst>>20)&0x1f, (inst>>25)&0x7f
        if funct3 in itype:
            return f"{itype[funct3]} x{rd}, x{rs1}, {imm}"
        if (funct3,funct7i) in ishift:
            return f"{ishift[(funct3,funct7i)]} x{rd}, x{rs1}, {shamt}"

    elif opcode == 0b0000011:  # Loads
        imm = sign_extend(inst>>20,12)
        if funct3 in loads:
            return f"{loads[funct3]} x{rd}, {imm}(x{rs1})"

    elif opcode == 0b0100011:  # Stores
        imm = sign_extend(((inst>>7)&0x1f)|(((inst>>25)&0x7f)<<5),12)
        if funct3 in stores:
            return f"{stores[funct3]} x{rs2}, {imm}(x{rs1})"

    elif opcode == 0b1100011:  # Branches
        imm = sign_extend((((inst>>7)&1)<<11)|(((inst>>8)&0xf)<<1)|
                          (((inst>>25)&0x3f)<<5)|(((inst>>31)&1)<<12),13)
        if funct3 in branches:
            return f"{branches[funct3]} x{rs1}, x{rs2}, {imm}"

    elif opcode == 0b1100111 and funct3==0x0:  # JALR
        return f"jalr x{rd}, {sign_extend(inst>>20,12)}(x{rs1})"

    elif opcode == 0b1101111:  # JAL
        imm = sign_extend((((inst>>21)&0x3ff)<<1)|(((inst>>20)&1)<<11)|
                          (((inst>>12)&0xff)<<12)|(((inst>>31)&1)<<20),21)
        return f"jal x{rd}, {imm}"

    elif opcode == 0b0110111:  # LUI
        return f"lui x{rd}, {inst & 0xfffff000}"

    elif opcode == 0b0010111:  # AUIPC
        return f"auipc x{rd}, {inst & 0xfffff000}"

    elif opcode == 0b1110011:  # SYSTEM
        return {0:"ecall",1:"ebreak"}.get(inst>>20, f".word 0x{inst:08x}")

    return f".word 0x{inst:08x}"


def disassemble(start_addr=0x80000000, end_addr=0x80008000, decode_flag=True):
    """Disassemble instructions from memory within a given address range."""
    lines, addr = [], start_addr
    while addr < end_addr:
        word = get_word(addr)
        if word == 0:  # skip empty
            addr += 4
            continue
        asm = decode(word) if decode_flag else ""
        line = f"{addr:08x}: {word:08x} {asm}"
        print(line)
        lines.append(line)
        addr += 4
    return lines
