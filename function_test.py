# Test helper function for Salsa20 cipher

def bsum(a, b, mode='int'):
    # Available modes: int, hex
    if mode == 'hex':
        a = int(a, 16)
        b = int(b, 16)
    result = (a+b) % 2**32
    return "0x{0:0{1}x}".format(result, 8)

def xor(a, b, mode='int'):
    # Available modes: int, hex
    if mode == 'hex':
        a = int(a, 16)
        b = int(b, 16)
    result = a ^ b
    return "0x{0:0{1}x}".format(result, 8)

def l_rot(val, bits, mode='int'):
    # Available modes: int, hex
    if mode == 'hex':
        val = int(val, 16)
    result = ((val << bits) | (val >> (val).bit_length()-bits)) & (2**(val).bit_length()-1)
    return "0x{0:0{1}x}".format(result, 8)

def littleendian(b0, b1, b2, b3):
    result = "0x{0:0{1}x}".format(b0 + 2**8*b1 + 2**16*b2 + 2**24*b3, 8)
    return result

if __name__ == '__main__':

    print("The sum:")
    print("0xc0a8787e + 0x9fd1161d = 0x60798e9b")
    print("{} + {} = {}\n".format('0xc0a8787e', '0x9fd1161d', bsum('0xc0a8787e', '0x9fd1161d', mode='hex')))

    print("The exclusive-or:")
    print("0xc0a8787e ⊕ 0x9fd1161d = 0x5f796e63")
    print("{} ⊕ {} = {}\n".format('0xc0a8787e', '0x9fd1161d', xor('0xc0a8787e', '0x9fd1161d', mode='hex')))

    print("The c-bit left rotation")
    print("0xc0a8787e <<< 5 = 0x150f0fd8")
    print("{} <<< {} = {}\n".format('0xc0a8787e', 5, l_rot('0xc0a8787e', 5, mode='hex')))

    print("Littleendian:")
    print("littleendian(0, 0, 0, 0) = 0x00000000")
    print("littleendian(0, 0, 0, 0) = {}".format(littleendian(0, 0, 0, 0)))
    print("littleendian(86, 75, 30, 9) = 0x091e4b56")
    print("littleendian(86, 75, 30, 9) = {}".format(littleendian(86, 75, 30, 9)))
    print("littleendian(255, 255, 255, 250) = 0xfaffffff")
    print("littleendian(255, 255, 255, 250) = {}".format(littleendian(255, 255, 255, 250)))