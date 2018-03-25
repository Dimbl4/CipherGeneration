# Test helper function for Salsa20 cipher

def bsum(a, b, mode='hex'):
    # Available modes: int, hex
    if mode == 'hex':
        a = int(a, 16)
        b = int(b, 16)
    result = (a+b) % 2**32
    return "0x{0:0{1}x}".format(result, 8)

def bxor(a, b, mode='hex'):
    # Available modes: int, hex
    if mode == 'hex':
        a = int(a, 16)
        b = int(b, 16)
    result = a ^ b
    return "0x{0:0{1}x}".format(result, 8)

def l_rot(val, bits, mode='hex'):
    # Available modes: int, hex
    if mode == 'hex':
        val = int(val, 16)
    tmp = bin(val)[2:].zfill(32)
    result = int(tmp[bits:] + tmp[:bits], 2)
    return "0x{0:0{1}x}".format(result, 8)

def quarterround(y0, y1, y2, y3):
    z1 = bxor(y1, l_rot(bsum(y0, y3), 7))
    z2 = bxor(y2, l_rot(bsum(z1, y0), 9))
    z3 = bxor(y3, l_rot(bsum(z2, z1), 13))
    z0 = bxor(y0, l_rot(bsum(z3, z2), 18))
    return z0, z1, z2, z3

def littleendian(b0, b1, b2, b3):
    result = "0x{0:0{1}x}".format(b0 + 2**8*b1 + 2**16*b2 + 2**24*b3, 8)
    return result

if __name__ == '__main__':

    print("The sum:")
    print("0xc0a8787e + 0x9fd1161d = 0x60798e9b")
    print("{} + {} = {}".format('0xc0a8787e', '0x9fd1161d', bsum('0xc0a8787e', '0x9fd1161d')))
    print("#"*80)
    print("The exclusive-or:")
    print("0xc0a8787e ⊕ 0x9fd1161d = 0x5f796e63")
    print("{} ⊕ {} = {}".format('0xc0a8787e', '0x9fd1161d', bxor('0xc0a8787e', '0x9fd1161d')))
    print("#"*80)
    print("The c-bit left rotation")
    print("0xc0a8787e <<< 5 = 0x150f0fd8")
    print("{} <<< {} = {}".format('0xc0a8787e', 5, l_rot('0xc0a8787e', 5)))
    print("#"*80)
    print("Quarterround:")
    print("""quarterround(0x00000000, 0x00000000, 0x00000000, 0x00000000)
    = (0x00000000, 0x00000000, 0x00000000, 0x00000000)""")
    print("""quarterround(0x00000000, 0x00000000, 0x00000000, 0x00000000)
    = {}""".format(quarterround('0x00000000', '0x00000000', '0x00000000', '0x00000000')))
    print()
    print("""quarterround(0x00000001, 0x00000000, 0x00000000, 0x00000000)
    = (0x08008145, 0x00000080, 0x00010200, 0x20500000)""")
    print("""quarterround(0x00000001, 0x00000000, 0x00000000, 0x00000000)
    = {}""".format(quarterround('0x00000001', '0x00000000', '0x00000000', '0x00000000')))
    print()
    print("""quarterround(0x00000000, 0x00000001, 0x00000000, 0x00000000
    = (0x88000100, 0x00000001, 0x00000200, 0x00402000)""")
    print("""quarterround(0x00000000, 0x00000001, 0x00000000, 0x00000000)
    = {}""".format(quarterround('0x00000000', '0x00000001', '0x00000000', '0x00000000')))
    print()
    print("""quarterround(0x00000000, 0x00000000, 0x00000001, 0x00000000
    = (0x80040000, 0x00000000, 0x00000001, 0x00002000)""")
    print("""quarterround(0x00000000, 0x00000000, 0x00000001, 0x00000000)
    = {}""".format(quarterround('0x00000000', '0x00000000', '0x00000001', '0x00000000')))
    print()
    print("""quarterround(0x00000000, 0x00000000, 0x00000000, 0x00000001
    = (0x00048044, 0x00000080, 0x00010000, 0x20100001)""")
    print("""quarterround(0x00000000, 0x00000000, 0x00000000, 0x00000001)
    = {}""".format(quarterround('0x00000000', '0x00000000', '0x00000000', '0x00000001')))
    print()
    print("""quarterround(0xe7e8c006, 0xc4f9417d, 0x6479b4b2, 0x68c67137
    = (0xe876d72b, 0x9361dfd5, 0xf1460244, 0x948541a3)""")
    print("""quarterround(0xe7e8c006, 0xc4f9417d, 0x6479b4b2, 0x68c67137)
    = {}""".format(quarterround('0xe7e8c006', '0xc4f9417d', '0x6479b4b2', '0x68c67137')))
    print()
    print("""quarterround(0xd3917c5b, 0x55f1c407, 0x52a58a7a, 0x8f887a3b
    = (0x3e2f308c, 0xd90a8f36, 0x6ab2a923, 0x2883524c)""")
    print("""quarterround(0xd3917c5b, 0x55f1c407, 0x52a58a7a, 0x8f887a3b)
    = {}""".format(quarterround('0xd3917c5b', '0x55f1c407', '0x52a58a7a', '0x8f887a3b')))

    print("#"*80)
    print("Littleendian:")
    print("littleendian(0, 0, 0, 0) = 0x00000000")
    print("littleendian(0, 0, 0, 0) = {}".format(littleendian(0, 0, 0, 0)))
    print("littleendian(86, 75, 30, 9) = 0x091e4b56")
    print("littleendian(86, 75, 30, 9) = {}".format(littleendian(86, 75, 30, 9)))
    print("littleendian(255, 255, 255, 250) = 0xfaffffff")
    print("littleendian(255, 255, 255, 250) = {}".format(littleendian(255, 255, 255, 250)))