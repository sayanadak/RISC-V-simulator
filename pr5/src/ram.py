
size = 1 << 32
ram ={}

def check_addr(a):
    if not isinstance(a, int) or a<0 or a>=size:
        raise ValueError(f"address {a} outof range [0, {size-1}]")
def read(addr):
        check_addr(addr)
        return ram.get(addr, 0)
def write(addr, data):
        check_addr(addr)
        ram[addr] = data & 0xFF 

