import sys
from disassembler import disassemble, load_bin_file_to_ram
from ram import read

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_bin_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    load_bin_file_to_ram(filepath)

    start_addr = 0x80000000
    print("text section (disassembled):")
    for line in disassemble(start_addr, end_addr=0x80008000):
        print(line)
    start_addr = 0x80008000
    print("data section (disassembled):")
    for line in disassemble(start_addr, end_addr=0x80010000, decode_flag=False):
        print(line)
if __name__ == "__main__":
    main()

