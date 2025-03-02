#!/usr/bin/env python3
import os
import random
import hashlib
from pathlib import Path


def get_random_lines(filename, quantity):
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line.strip())

    random_lines = []
    for x in range(quantity):
        random_lines.append(lines[random.randint(0, quantity - 1)])
    return random_lines


def validate():
    try:
        import findBlockNonce
    except ImportError:
        raise ImportError("Could not import homework file 'findBlockNonce.py'")

    required_methods = ["mine_block"]
    for m in required_methods:
        if m not in dir(findBlockNonce):
            print("%s not defined" % m)
            return 0

    num_tests = 5
    num_passed = 0
    filename = Path(__file__).parent.absolute()
    filename = filename.joinpath("ethereum_txt.txt")

    for i in range(num_tests):
        print("=========== Running test %d ===========" % (i + 1))
        numbits = random.SystemRandom().randint(10, 20)
        numtrans = random.SystemRandom().randint(5, 15)
        rand_lines = get_random_lines(filename, numtrans)

        prev_block = os.urandom(32)
        print(f"This block has {numtrans} transactions")
        try:
            nonce = findBlockNonce.mine_block(numbits, prev_block, rand_lines)
        except Exception as e:
            print(f"mine_block failed\n{e}")
            continue
        print("mine_block ran successfully")

        if not isinstance(nonce, bytes):
            print("mine_block should return bytes")
            continue
        print("mine_block returned byte strings (as it should)")

        h = hashlib.new('sha256')
        h.update(prev_block)
        for line in rand_lines:
            h.update(line.encode())
        h.update(nonce)
        h_hex = h.hexdigest()
        h_bin = bin(int(h_hex, base=16))[2:]

        difficulty = ''
        for _ in range(numbits):
            difficulty = difficulty + '0'

        if h_bin[-numbits:] == difficulty:
            num_passed = num_passed + 1
            print("SUCCESS: You found a valid nonce")
        else:
            print("ERROR: You failed to find a valid nonce")

    print(f"\nScore = {int(num_passed * (100 / num_tests))}%")
    return int(num_passed * (100 / num_tests))


if __name__ == "__main__":
    final_score = validate()
    print(f"Score = {final_score}%")
