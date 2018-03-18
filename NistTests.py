import math
import scipy.special as spc
import scipy.fftpack as sff
import numpy as np
from BinaryMatrix import BinaryMatrix

class NistTest():

    def monobit(self, bin_data: str):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

        The focus of this test is the proportion of zeros and ones for the entire sequence. The purpose of this test is
        to determine whether the number of ones and zeros in a sequence are approximately the same as would be expected
        for a truly random sequence. This test assesses the closeness of the fraction of ones to 1/2, that is the number
        of ones and zeros ina  sequence should be about the same. All subsequent tests depend on this test.

        :param bin_data: a binary string
        :return: the p-value from the test
        """
        count = 0
        # If the char is 0 minus 1, else add 1
        for char in bin_data:
            if char == '0':
                count -= 1
            else:
                count += 1
        # Calculate the p value
        sobs = count / math.sqrt(len(bin_data))
        p_val = spc.erfc(math.fabs(sobs) / math.sqrt(2))
        return p_val

    def block_frequency(self, bin_data: str, block_size=128):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this tests is the proportion of ones within M-bit blocks. The purpose of this tests is to determine
        whether the frequency of ones in an M-bit block is approximately M/2, as would be expected under an assumption
        of randomness. For block size M=1, this test degenerates to the monobit frequency test.
        :param bin_data: a binary string
        :return: the p-value from the test
        :param block_size: the size of the blocks that the binary sequence is partitioned into
        """
        # Work out the number of blocks, discard the remainder
        num_blocks = math.floor(len(bin_data) / block_size)
        block_start, block_end = 0, block_size
        # Keep track of the proportion of ones per block
        proportion_sum = 0.0
        for i in range(num_blocks):
            # Slice the binary string into a block
            block_data = bin_data[block_start:block_end]
            # Keep track of the number of ones
            ones_count = 0
            for char in block_data:
                if char == '1':
                    ones_count += 1
            pi = ones_count / block_size
            proportion_sum += pow(pi - 0.5, 2.0)
            # Update the slice locations
            block_start += block_size
            block_end += block_size
        # Calculate the p-value
        chi_squared = 4.0 * block_size * proportion_sum
        p_val = spc.gammaincc(num_blocks / 2, chi_squared / 2)
        return p_val

    def independent_runs(self, bin_data: str):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this tests if the total number of runs in the sequences, where a run is an uninterrupted sequence
        of identical bits. A run of length k consists of k identical bits and is bounded before and after with a bit of
        the opposite value. The purpose of the runs tests is to determine whether the number of runs of ones and zeros
        of various lengths is as expected for a random sequence. In particular, this tests determines whether the
        oscillation between zeros and ones is either too fast or too slow.
        :param bin_data: a binary string
        :return: the p-value from the test
        """
        ones_count, n = 0, len(bin_data)
        for char in bin_data:
            if char == '1':
                ones_count += 1
        p, vobs = float(ones_count / n), 1
        tau = 2 / math.sqrt(len(bin_data))
        if abs(p - 0.5) > tau:
            return 0.0
        else:
            for i in range(1, n):
                if bin_data[i] != bin_data[i - 1]:
                    vobs += 1
            # expected_runs = 1 + 2 * (n - 1) * 0.5 * 0.5
            # print("\t" + "Observed runs =", vobs, "Expected runs", expected_runs)
            num = abs(vobs - 2.0 * n * p * (1.0 - p))
            den = 2.0 * math.sqrt(2.0 * n) * p * (1.0 - p)
            p_val = spc.erfc(float(num / den))
            return p_val

    def longest_runs(self, bin_data: str):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of the tests is the longest run of ones within M-bit blocks. The purpose of this tests is to determine
        whether the length of the longest run of ones within the tested sequences is consistent with the length of the
        longest run of ones that would be expected in a random sequence. Note that an irregularity in the expected
        length of the longest run of ones implies that there is also an irregularity ub tge expected length of the long
        est run of zeroes. Therefore, only one test is necessary for this statistical tests of randomness
        :param bin_data: a binary string
        :return: the p-value from the test
        """
        if len(bin_data) < 128:
            print("\t", "Not enough data to run test!")
            return -1.0
        elif len(bin_data) < 6272:
            k, m = 3, 8
            v_values = [1, 2, 3, 4]
            pik_values = [0.21484375, 0.3671875, 0.23046875, 0.1875]
        elif len(bin_data) < 75000:
            k, m = 5, 128
            v_values = [4, 5, 6, 7, 8, 9]
            pik_values = [0.1174035788, 0.242955959, 0.249363483, 0.17517706, 0.102701071, 0.112398847]
        else:
            k, m = 6, 10000
            v_values = [10, 11, 12, 13, 14, 15, 16]
            pik_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

        # Work out the number of blocks, discard the remainder
        # pik = [0.2148, 0.3672, 0.2305, 0.1875]
        num_blocks = math.floor(len(bin_data) / m)
        frequencies = np.zeros(k + 1)
        block_start, block_end = 0, m
        for i in range(num_blocks):
            # Slice the binary string into a block
            block_data = bin_data[block_start:block_end]
            # Keep track of the number of ones
            max_run_count, run_count = 0, 0
            for j in range(0, m):
                if block_data[j] == '1':
                    run_count += 1
                    max_run_count = max(max_run_count, run_count)
                else:
                    max_run_count = max(max_run_count, run_count)
                    run_count = 0
            max_run_count = max(max_run_count, run_count)
            if max_run_count < v_values[0]:
                frequencies[0] += 1
            for j in range(k):
                if max_run_count == v_values[j]:
                    frequencies[j] += 1
            if max_run_count > v_values[k - 1]:
                frequencies[k] += 1
            block_start += m
            block_end += m
        # print(frequencies)
        chi_squared = 0
        for i in range(len(frequencies)):
            chi_squared += (pow(frequencies[i] - (num_blocks * pik_values[i]), 2.0)) / (num_blocks * pik_values[i])
        p_val = spc.gammaincc(float(k / 2), float(chi_squared / 2))
        return p_val

    def matrix_rank(self, bin_data: str, q=32):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of the test is the rank of disjoint sub-matrices of the entire sequence. The purpose of this test is
        to check for linear dependence among fixed length sub strings of the original sequence. Note that this test
        also appears in the DIEHARD battery of tests.
        :param bin_data: a binary string
        :return: the p-value from the test
        """
        shape = (q, q)
        n = len(bin_data)
        block_size = int(q * q)
        num_m = math.floor(n / (q * q))
        block_start, block_end = 0, block_size
        # print(q, n, num_m, block_size)

        if num_m > 0:
            max_ranks = [0, 0, 0]
            for im in range(num_m):
                block_data = bin_data[block_start:block_end]
                block = np.zeros(len(block_data))
                for i in range(len(block_data)):
                    if block_data[i] == '1':
                        block[i] = 1.0
                m = block.reshape(shape)
                ranker = BinaryMatrix(m, q, q)
                rank = ranker.compute_rank()
                # print(rank)
                if rank == q:
                    max_ranks[0] += 1
                elif rank == (q - 1):
                    max_ranks[1] += 1
                else:
                    max_ranks[2] += 1
                # Update index trackers
                block_start += block_size
                block_end += block_size

            piks = [1.0, 0.0, 0.0]
            for x in range(1, 50):
                piks[0] *= 1 - (1.0 / (2 ** x))
            piks[1] = 2 * piks[0]
            piks[2] = 1 - piks[0] - piks[1]

            chi = 0.0
            for i in range(len(piks)):
                chi += pow((max_ranks[i] - piks[i] * num_m), 2.0) / (piks[i] * num_m)
            p_val = math.exp(-chi / 2)
            return p_val
        else:
            return -1.0

    def spectral(self, bin_data: str):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this test is the peak heights in the Discrete Fourier Transform of the sequence. The purpose of
        this test is to detect periodic features (i.e., repetitive patterns that are near each other) in the tested
        sequence that would indicate a deviation from the assumption of randomness. The intention is to detect whether
        the number of peaks exceeding the 95 % threshold is significantly different than 5 %.
        :param bin_data: a binary string
        :return: the p-value from the test
        """
        n = len(bin_data)
        plus_minus_one = []
        for char in bin_data:
            if char == '0':
                plus_minus_one.append(-1)
            elif char == '1':
                plus_minus_one.append(1)
        # Product discrete fourier transform of plus minus one
        s = sff.fft(plus_minus_one)
        modulus = np.abs(s[0:n // 2])
        tau = np.sqrt(np.log(1 / 0.05) * n)
        # Theoretical number of peaks
        count_n0 = 0.95 * (n / 2)
        # Count the number of actual peaks m > T
        count_n1 = len(np.where(modulus < tau)[0])
        # Calculate d and return the p value statistic
        d = (count_n1 - count_n0) / np.sqrt(n * 0.95 * 0.05 / 4)
        p_val = spc.erfc(abs(d) / np.sqrt(2))
        return p_val

    def non_overlapping_patterns(self, bin_data: str, pattern="000000001", num_blocks=8):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this test is the number of occurrences of pre-specified target strings. The purpose of this
        test is to detect generators that produce too many occurrences of a given non-periodic (aperiodic) pattern.
        For this test and for the Overlapping Template Matching test of Section 2.8, an m-bit window is used to
        search for a specific m-bit pattern. If the pattern is not found, the window slides one bit position. If the
        pattern is found, the window is reset to the bit after the found pattern, and the search resumes.
        :param bin_data: a binary string
        :param pattern: the pattern to match to
        :return: the p-value from the test
        """
        n = len(bin_data)
        pattern_size = len(pattern)
        block_size = math.floor(n / num_blocks)
        pattern_counts = np.zeros(num_blocks)
        # For each block in the data
        for i in range(num_blocks):
            block_start = i * block_size
            block_end = block_start + block_size
            block_data = bin_data[block_start:block_end]
            # Count the number of pattern hits
            j = 0
            while j < block_size:
                sub_block = block_data[j:j + pattern_size]
                if sub_block == pattern:
                    pattern_counts[i] += 1
                    j += pattern_size
                else:
                    j += 1
        # Calculate the theoretical mean and variance
        mean = (block_size - pattern_size + 1) / pow(2, pattern_size)
        var = block_size * ((1 / pow(2, pattern_size)) - (((2 * pattern_size) - 1) / (pow(2, pattern_size * 2))))
        # Calculate the Chi Squared statistic for these pattern matches
        chi_squared = 0
        for i in range(num_blocks):
            chi_squared += pow(pattern_counts[i] - mean, 2.0) / var
        # Calculate and return the p value statistic
        p_val = spc.gammaincc(num_blocks / 2, chi_squared / 2)
        return p_val