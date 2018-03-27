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

def quarterround(*args):
    (y0, y1, y2, y3) = args[0]
    z1 = bxor(y1, l_rot(bsum(y0, y3), 7))
    z2 = bxor(y2, l_rot(bsum(z1, y0), 9))
    z3 = bxor(y3, l_rot(bsum(z2, z1), 13))
    z0 = bxor(y0, l_rot(bsum(z3, z2), 18))
    return [z0, z1, z2, z3]

def rowround(*args):
    (y0, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15) = args[0]
    z0, z1, z2, z3 = quarterround([y0, y1, y2, y3])
    z5, z6, z7, z4 = quarterround([y5, y6, y7, y4])
    z10, z11, z8, z9 = quarterround([y10, y11, y8, y9])
    z15, z12, z13, z14 = quarterround([y15, y12, y13, y14])
    return [z0, z1, z2, z3, z4, z5, z6, z7, z8, z9, z10, z11, z12, z13, z14, z15]

def columnround(*args):
    (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15) = args[0]
    y0, y4, y8, y12 = quarterround([x0, x4, x8, x12])
    y5, y9, y13, y1 = quarterround([x5, x9, x13, x1])
    y10, y14, y2, y6 = quarterround([x10, x14, x2, x6])
    y15, y3, y7, y11 = quarterround([x15, x3, x7, x11])
    return [y0, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15]

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
    = {}""".format(quarterround(['0x00000000', '0x00000000', '0x00000000', '0x00000000'])))
    print()
    print("""quarterround(0x00000001, 0x00000000, 0x00000000, 0x00000000)
    = (0x08008145, 0x00000080, 0x00010200, 0x20500000)""")
    print("""quarterround(0x00000001, 0x00000000, 0x00000000, 0x00000000)
    = {}""".format(quarterround(['0x00000001', '0x00000000', '0x00000000', '0x00000000'])))
    print()
    print("""quarterround(0x00000000, 0x00000001, 0x00000000, 0x00000000
    = (0x88000100, 0x00000001, 0x00000200, 0x00402000)""")
    print("""quarterround(0x00000000, 0x00000001, 0x00000000, 0x00000000)
    = {}""".format(quarterround(['0x00000000', '0x00000001', '0x00000000', '0x00000000'])))
    print()
    print("""quarterround(0x00000000, 0x00000000, 0x00000001, 0x00000000
    = (0x80040000, 0x00000000, 0x00000001, 0x00002000)""")
    print("""quarterround(0x00000000, 0x00000000, 0x00000001, 0x00000000)
    = {}""".format(quarterround(['0x00000000', '0x00000000', '0x00000001', '0x00000000'])))
    print()
    print("""quarterround(0x00000000, 0x00000000, 0x00000000, 0x00000001
    = (0x00048044, 0x00000080, 0x00010000, 0x20100001)""")
    print("""quarterround(0x00000000, 0x00000000, 0x00000000, 0x00000001)
    = {}""".format(quarterround(['0x00000000', '0x00000000', '0x00000000', '0x00000001'])))
    print()
    print("""quarterround(0xe7e8c006, 0xc4f9417d, 0x6479b4b2, 0x68c67137
    = (0xe876d72b, 0x9361dfd5, 0xf1460244, 0x948541a3)""")
    print("""quarterround(0xe7e8c006, 0xc4f9417d, 0x6479b4b2, 0x68c67137)
    = {}""".format(quarterround(['0xe7e8c006', '0xc4f9417d', '0x6479b4b2', '0x68c67137'])))
    print()
    print("""quarterround(0xd3917c5b, 0x55f1c407, 0x52a58a7a, 0x8f887a3b
    = (0x3e2f308c, 0xd90a8f36, 0x6ab2a923, 0x2883524c)""")
    print("""quarterround(0xd3917c5b, 0x55f1c407, 0x52a58a7a, 0x8f887a3b)
    = {}""".format(quarterround(['0xd3917c5b', '0x55f1c407', '0x52a58a7a', '0x8f887a3b'])))

    # rowround
    print("#"*80)
    print("Rowround:")
    print(['0x08008145', '0x00000080', '0x00010200', '0x20500000',
            '0x20100001', '0x00048044', '0x00000080', '0x00010000',
            '0x00000001', '0x00002000', '0x80040000', '0x00000000',
            '0x00000001', '0x00000200', '0x00402000', '0x88000100'])
    print(rowround(['0x00000001', '0x00000000', '0x00000000', '0x00000000',
                    '0x00000001', '0x00000000', '0x00000000', '0x00000000',
                    '0x00000001', '0x00000000', '0x00000000', '0x00000000',
                    '0x00000001', '0x00000000', '0x00000000', '0x00000000']))
    print()
    print(['0xa890d39d', '0x65d71596', '0xe9487daa', '0xc8ca6a86',
            '0x949d2192', '0x764b7754', '0xe408d9b9', '0x7a41b4d1',
            '0x3402e183', '0x3c3af432', '0x50669f96', '0xd89ef0a8',
            '0x0040ede5', '0xb545fbce', '0xd257ed4f', '0x1818882d'])
    print(rowround(['0x08521bd6', '0x1fe88837', '0xbb2aa576', '0x3aa26365',
                    '0xc54c6a5b', '0x2fc74c2f', '0x6dd39cc3', '0xda0a64f6',
                    '0x90a2f23d', '0x067f95a6', '0x06b35f61', '0x41e4732e',
                    '0xe859c100', '0xea4d84b7', '0x0f619bff', '0xbc6e965a']))

    # columnround
    print("#"*80)
    print("Columnround:")
    print(['0x10090288', '0x00000000', '0x00000000', '0x00000000',
           '0x00000101', '0x00000000', '0x00000000', '0x00000000',
           '0x00020401', '0x00000000', '0x00000000', '0x00000000',
           '0x40a04001', '0x00000000', '0x00000000', '0x00000000'])
    print(columnround(['0x00000001', '0x00000000', '0x00000000', '0x00000000',
                    '0x00000001', '0x00000000', '0x00000000', '0x00000000',
                    '0x00000001', '0x00000000', '0x00000000', '0x00000000',
                    '0x00000001', '0x00000000', '0x00000000', '0x00000000']))
    print()
    print(['0x8c9d190a', '0xce8e4c90', '0x1ef8e9d3', '0x1326a71a',
           '0x90a20123', '0xead3c4f3', '0x63a091a0', '0xf0708d69',
           '0x789b010c', '0xd195a681', '0xeb7d5504', '0xa774135c',
           '0x481c2027', '0x53a8e4b5', '0x4c1f89c5', '0x3f78c9c8'])
    print(columnround(['0x08521bd6', '0x1fe88837', '0xbb2aa576', '0x3aa26365',
                       '0xc54c6a5b', '0x2fc74c2f', '0x6dd39cc3', '0xda0a64f6',
                       '0x90a2f23d', '0x067f95a6', '0x06b35f61', '0x41e4732e',
                       '0xe859c100', '0xea4d84b7', '0x0f619bff', '0xbc6e965a']))

    print("#"*80)
    print("Littleendian:")
    print("littleendian(0, 0, 0, 0) = 0x00000000")
    print("littleendian(0, 0, 0, 0) = {}".format(littleendian(0, 0, 0, 0)))
    print("littleendian(86, 75, 30, 9) = 0x091e4b56")
    print("littleendian(86, 75, 30, 9) = {}".format(littleendian(86, 75, 30, 9)))
    print("littleendian(255, 255, 255, 250) = 0xfaffffff")
    print("littleendian(255, 255, 255, 250) = {}".format(littleendian(255, 255, 255, 250)))


