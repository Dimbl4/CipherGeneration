# Test helper function for Salsa20 cipher
import time

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

def doubleround(*args):
    # (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15) =
    return rowround(columnround(args[0]))

def littleendian(*args):
    (b0, b1, b2, b3) = args[0]
    result = "0x{0:0{1}x}".format(b0 + 2**8*b1 + 2**16*b2 + 2**24*b3, 8)
    return result

def littleendian_reverse(word, mode='hex'):
    if mode=='int':
        word = hex(word)
    b0 = int(word[2:4], 16)
    b1 = int(word[4:6], 16)
    b2 = int(word[6:8], 16)
    b3 = int(word[8:10], 16)
    return [b0, b1, b2, b3]

def salsa20(*args, times=1):
    for _ in range(times):
        if _ >= 1:
            X = little_reverse
        elif _ == 0:
            X = args[0]
        x = []
        for i in range(16):
            x.append(littleendian(X[4*i:4*i+4]))
        z = x
        for _ in range(10):
            z = doubleround(z)

        little_reverse = []
        for i in range(16):
            for value in reversed(littleendian_reverse(bsum(x[i], z[i]))):
                little_reverse.append(value)

    return little_reverse

def salsa20_key(n, k0, k1=None):
    sigma0 = [101, 120, 112, 97]
    sigma1 = [110, 100, 32, 51]
    sigma2 = [50, 45, 98, 121]
    sigma3 = [116, 101, 32, 107]
    tau0 = [101, 120, 112, 97]
    tau1 = [110, 100, 32, 49]
    tau2 = [54, 45, 98, 121]
    tau3 = [116, 101, 32, 107]

    if k1 == None:
        args = tau0 + k0 + tau1 + n + tau2 + k0 + tau3
    else:
        args = tau0 + k0 + sigma1 + n + sigma2 + k1 + sigma3
    return salsa20(args)


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
    # doubleround
    print("#"*80)
    print("Doubleround:")
    print(['0x8186a22d', '0x0040a284', '0x82479210', '0x06929051',
           '0x08000090', '0x02402200', '0x00004000', '0x00800000',
           '0x00010200', '0x20400000', '0x08008104', '0x00000000',
           '0x20500000', '0xa0000040', '0x0008180a', '0x612a8020'])
    print(doubleround(['0x00000001', '0x00000000', '0x00000000', '0x00000000',
                       '0x00000000', '0x00000000', '0x00000000', '0x00000000',
                       '0x00000000', '0x00000000', '0x00000000', '0x00000000',
                       '0x00000000', '0x00000000', '0x00000000', '0x00000000']))
    print()
    print(['0xccaaf672', '0x23d960f7', '0x9153e63a', '0xcd9a60d0',
           '0x50440492', '0xf07cad19', '0xae344aa0', '0xdf4cfdfc',
           '0xca531c29', '0x8e7943db', '0xac1680cd', '0xd503ca00',
           '0xa74b2ad6', '0xbc331c5c', '0x1dda24c7', '0xee928277'])
    print(doubleround(['0xde501066', '0x6f9eb8f7', '0xe4fbbd9b', '0x454e3f57',
                       '0xb75540d3', '0x43e93a4c', '0x3a6f2aa0', '0x726d6b36',
                       '0x9243f484', '0x9145d1e8', '0x4fa9d247', '0xdc8dee11',
                       '0x054bf545', '0x254dd653', '0xd9421b6d', '0x67b276c1']))
    print("#"*80)
    print("Littleendian:")
    print("littleendian(0, 0, 0, 0) = 0x00000000")
    print("littleendian(0, 0, 0, 0) = {}".format(littleendian([0, 0, 0, 0])))
    print("littleendian(86, 75, 30, 9) = 0x091e4b56")
    print("littleendian(86, 75, 30, 9) = {}".format(littleendian([86, 75, 30, 9])))
    print("littleendian(255, 255, 255, 250) = 0xfaffffff")
    print("littleendian(255, 255, 255, 250) = {}".format(littleendian([255, 255, 255, 250])))

    print("#"*80)
    print("Salsa20:")
    print([109, 42,178,168,156,240,248,238,168,196,190,203, 26,110,170,154,
       29, 29,150, 26,150, 30,235,249,190,163,251, 48, 69,144, 51, 57,
       118, 40,152,157,180, 57, 27, 94,107, 42,236, 35, 27,111,114,114,
       219,236,232,135,111,155,110, 18, 24,232, 95,158,179, 19, 48,202])
    print(salsa20([211,159, 13,115, 76, 55, 82,183, 3,117,222, 37,191,187,234,136,
                          49,237,179, 48, 1,106,178,219,175,199,166, 48, 86, 16,179,207,
                          31,240, 32, 63, 15, 83, 93,161,116,147, 48,113,238, 55,204, 36,
                          79,201,235, 79, 3, 81,156, 47,203, 26,244,243, 88,118,104, 54]))
    print()
    print([179, 19, 48,202,219,236,232,135,111,155,110, 18, 24,232, 95,158,
           26,110,170,154,109, 42,178,168,156,240,248,238,168,196,190,203,
           69,144, 51, 57, 29, 29,150, 26,150, 30,235,249,190,163,251, 48,
           27,111,114,114,118, 40,152,157,180, 57, 27, 94,107, 42,236, 35])
    print(salsa20([88,118,104, 54, 79,201,235, 79, 3, 81,156, 47,203, 26,244,243,
                   191,187,234,136,211,159, 13,115, 76, 55, 82,183, 3,117,222, 37,
                   86, 16,179,207, 49,237,179, 48, 1,106,178,219,175,199,166, 48,
                   238, 55,204, 36, 31,240, 32, 63, 15, 83, 93,161,116,147, 48,113]))

    # print()
    # start = time.time()
    # print([8, 18, 38,199,119, 76,215, 67,173,127,144,162,103,212,176,217,
    #        192, 19,233, 33,159,197,154,160,128,243,219, 65,171,136,135,225,
    #        123, 11, 68, 86,237, 82, 20,155,133,189, 9, 83,167,116,194, 78,
    #        122,127,195,185,185,204,188, 90,245, 9,183,248,226, 85,245,104])
    # print(salsa20([6,124, 83,146, 38,191, 9, 50, 4,161, 47,222,122,182,223,185,
    #                75, 27, 0,216, 16,122, 7, 89,162,104,101,147,213, 21, 54, 95,
    #                225,253,139,176,105,132, 23,116, 76, 41,176,207,221, 34,157,108,
    #                94, 94, 99, 52, 90,117, 91,220,146,190,239,143,196,176,130,186], times=1000000))
    # end = time.time()
    # print(end - start)

    print("#"*80)
    print("Salsa20k0k1(n):")
    k0 = list(range(1, 17))
    k1 = list(range(201, 217))
    n = list(range(101, 117))
    print([69, 37, 68, 39, 41, 15,107,193,255,139,122, 6,170,233,217, 98,
           89,144,182,106, 21, 51,200, 65,239, 49,222, 34,215,114, 40,126,
           104,197, 7,225,197,153, 31, 2,102, 78, 76,176, 84,245,246,184,
           177,160,133,130, 6, 72,149,119,192,195,132,236,234,103,246, 74])

    print(salsa20_key(n, k0, k1))
    print("Salsa20k0(n):")
    print([39,173, 46,248, 30,200, 82, 17, 48, 67,254,239, 37, 18, 13,247,
           241,200, 61,144, 10, 55, 50,185, 6, 47,246,253,143, 86,187,225,
           134, 85,110,246,161,163, 43,235,231, 94,171, 51,145,214,112, 29,
           14,232, 5, 16,151,140,183,141,171, 9,122,181,104,182,177,193])
    print(salsa20_key(n, k0))