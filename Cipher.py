from tqdm import tqdm
from math import floor
import numpy as np

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
        # if mode == 'hex':
        #     a = int(a, 16)
        #     b = int(b, 16)
        result = (a+b) % 2**32
        return result

    def bxor(self, a, b, mode='int'):
        # Available modes: int, hex
        result = a ^ b
        return result

    def l_rot(self, val, bits, mode='int'):
        # Available modes: int, hex
        tmp = "{0:032b}".format(val)
        result = int(tmp[bits:] + tmp[:bits], 2)
        return result

    def row_roll(self, arr, roll_list):
        return np.array([np.roll(arr, x) for arr, x in zip(arr, roll_list)])

    def column_roll(self, arr, roll_list):
        return np.array([np.roll(arr, x, axis=0) for arr, x in zip(arr, roll_list)])

    def quarterround(self, y):
        z = [0]*4
        z[1] = self.bxor(y[1], self.l_rot(self.bsum(y[0], y[3]), 7))
        z[2] = self.bxor(y[2], self.l_rot(self.bsum(z[1], y[0]), 9))
        z[3] = self.bxor(y[3], self.l_rot(self.bsum(z[2], z[1]), 13))
        z[0] = self.bxor(y[0], self.l_rot(self.bsum(z[3], z[2]), 18))
        return z

    def rowround(self, y):
        y = np.array(y).reshape(4, 4)
        y_rolled = self.row_roll(y, [0, -1, -2, -3])
        z0, z1, z2, z3 = self.quarterround(y_rolled[0,:])
        z5, z6, z7, z4 = self.quarterround(y_rolled[1,:])
        z10, z11, z8, z9 = self.quarterround(y_rolled[2,:])
        z15, z12, z13, z14 = self.quarterround(y_rolled[3,:])
        return [z0, z1, z2, z3, z4, z5, z6, z7, z8, z9, z10, z11, z12, z13, z14, z15]

    def columnround(self, *args):
        (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15) = args[0]
        y0, y4, y8, y12 = self.quarterround([x0, x4, x8, x12])
        y5, y9, y13, y1 = self.quarterround([x5, x9, x13, x1])
        y10, y14, y2, y6 = self.quarterround([x10, x14, x2, x6])
        y15, y3, y7, y11 = self.quarterround([x15, x3, x7, x11])
        return [y0, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15]

    def doubleround(self, *args):
        return self.rowround(self.columnround(args[0]))

    def littleendian(self, *args, mode='int'):
        (b0, b1, b2, b3) = args[0]
        result = b0 + 2**8*b1 + 2**16*b2 + 2**24*b3
        return result

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