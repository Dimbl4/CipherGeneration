from tqdm import tqdm
from math import floor

class Cipher():
    sigma0 = [101, 120, 112, 97]
    sigma1 = [110, 100, 32, 51]
    sigma2 = [50, 45, 98, 121]
    sigma3 = [116, 101, 32, 107]
    tau0 = [101, 120, 112, 97]
    tau1 = [110, 100, 32, 49]
    tau2 = [54, 45, 98, 121]
    tau3 = [116, 101, 32, 107]

    def __init__(self, k0, k1=None, nonce=[0]*8, count=[0]*8):
        self.k0 = k0
        self.k1 = k1
        self.nonce = nonce
        self.count = count
        pass

    def bsum(self, a, b, mode='int'):
        # Available modes: int, hex
        if mode == 'hex':
            a = int(a, 16)
            b = int(b, 16)
        result = (a+b) % 2**32
        if mode == 'int':
            return result
        else:
            return "0x{0:0{1}x}".format(result, 8)

    def bxor(self, a, b, mode='int'):
        # Available modes: int, hex
        if mode == 'hex':
            a = int(a, 16)
            b = int(b, 16)
        result = a ^ b
        if mode=='int':
            return result
        else:
            return "0x{0:0{1}x}".format(result, 8)

    def l_rot(self, val, bits, mode='int'):
        # Available modes: int, hex
        if mode == 'hex':
            val = int(val, 16)
        tmp = bin(val)[2:].zfill(32)
        result = int(tmp[bits:] + tmp[:bits], 2)
        if mode == 'int':
            return result
        else:
            return "0x{0:0{1}x}".format(result, 8)

    def quarterround(self, *args):
        (y0, y1, y2, y3) = args[0]
        z1 = self.bxor(y1, self.l_rot(self.bsum(y0, y3), 7))
        z2 = self.bxor(y2, self.l_rot(self.bsum(z1, y0), 9))
        z3 = self.bxor(y3, self.l_rot(self.bsum(z2, z1), 13))
        z0 = self.bxor(y0, self.l_rot(self.bsum(z3, z2), 18))
        return [z0, z1, z2, z3]

    def rowround(self, *args):
        (y0, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15) = args[0]
        z0, z1, z2, z3 = self.quarterround([y0, y1, y2, y3])
        z5, z6, z7, z4 = self.quarterround([y5, y6, y7, y4])
        z10, z11, z8, z9 = self.quarterround([y10, y11, y8, y9])
        z15, z12, z13, z14 = self.quarterround([y15, y12, y13, y14])
        return [z0, z1, z2, z3, z4, z5, z6, z7, z8, z9, z10, z11, z12, z13, z14, z15]

    def columnround(self, *args):
        (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15) = args[0]
        y0, y4, y8, y12 = self.quarterround([x0, x4, x8, x12])
        y5, y9, y13, y1 = self.quarterround([x5, x9, x13, x1])
        y10, y14, y2, y6 = self.quarterround([x10, x14, x2, x6])
        y15, y3, y7, y11 = self.quarterround([x15, x3, x7, x11])
        return [y0, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15]

    def doubleround(self, *args):
        # (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15) =
        return self.rowround(self.columnround(args[0]))

    def littleendian(self, *args, mode='int'):
        (b0, b1, b2, b3) = args[0]
        result = b0 + 2**8*b1 + 2**16*b2 + 2**24*b3
        if mode=='int':
            return result
        else:
            return "0x{0:0{1}x}".format(result, 8)

    def littleendian_reverse(self, word, mode='int'):
        if mode=='int':
            word = "0x{0:0{1}x}".format(word, 8)
        b0 = int(word[2:4], 16)
        b1 = int(word[4:6], 16)
        b2 = int(word[6:8], 16)
        b3 = int(word[8:10], 16)
        return [b0, b1, b2, b3]

    def littleendian_reverse_16(self, number):
        string =  "0x{0:0{1}x}".format(number, 16)
        b = []
        for s0, s1 in zip(string[0::2], string[1::2]):
            if s0+s1!='0x':
                b.append(int(s0+s1, 16))
            else:
                continue
        return b

    def cipher(self, *args, times=1):
        for _ in range(times):
            if _ >= 1:
                X = little_reverse
            elif _ == 0:
                X = args[0]
            x = []
            for i in range(16):
                x.append(self.littleendian(X[4*i:4*i+4]))
            z = x
            for _ in range(10):
                z = self.doubleround(z)

            little_reverse = []
            for i in range(16):
                for value in reversed(self.littleendian_reverse(self.bsum(x[i], z[i]))):
                    little_reverse.append(value)
        return little_reverse

    def get_cipher(self, times=1):
        cipher_stream = []
        if self.k1 == None:
            for i in tqdm(range(times)):
                count = self.littleendian_reverse_16(floor(i/64))
                self.args = self.tau0 + self.k0 + self.tau1 + self.nonce + count + self.tau2 + self.k0 + self.tau3
                cipher_stream.append(self.cipher(self.args)[i % 64])
        else:
            for i in tqdm(range(times)):
                count = self.littleendian_reverse(floor(i/64))
                self.args = self.sigma0 + self.k0 + self.sigma1 + self.nonce + count + self.sigma2 + self.k1 + self.sigma3
                cipher_stream.append(self.cipher(self.args)[i % 64])

        return cipher_stream