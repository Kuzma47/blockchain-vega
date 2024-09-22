KEYS_IN_USAGE = 10**7
KEY_LENGTH = 256

total_keys = 10**KEY_LENGTH
p = KEYS_IN_USAGE / total_keys

print(f'Chance of generating 1 of existing keys with length {KEY_LENGTH} is {p}')


'''
10^7 / 10^256 = 10^(7-256) = 1/10^249
'''
