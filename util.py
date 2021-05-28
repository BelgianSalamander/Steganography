def bits_to_int(bits):
    b = 0
    for n in bits:
        b = b * 2 + n
    return b

def int_to_bits(n, length = 64):
    bits = [n & 1<<i for i in range(length-1,-1,-1)]
    return [1 if k > 0 else 0 for k in bits]