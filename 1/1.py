import time


def shuffle_bits(hash_value: int, shift: int, prime: int = 16777619) -> int:
    hash_value = (hash_value * prime) & 0xFFFFFFFF
    return hash_value ^ (hash_value >> shift)


def my_hash(s: str) -> int:
    hash_value = 42
    for i, char in enumerate(s):
        hash_value ^= (ord(char) << (i % 4)) & 0xFFFFFFFF
        hash_value = shuffle_bits(shuffle_bits(hash_value, 13), 17)
    return hash_value


# 1
h1 = my_hash("hello")
h2 = my_hash("hello")
print(h1 == h2)

# 2
h1 = my_hash("a")
h2 = my_hash("b")
print(h1, h2)

# 3
start_time = time.time()
long_string = "very long string" * 1000
h = my_hash(long_string)
end_time = time.time()
print(f"Length: {len(long_string)} Hash: {h} Time: {1000 * round(end_time - start_time, 4) } ms")

'''
Приемущества
- Простота реализации
- Высокая производительность (линейная)
- Ограничение на 32 бита

Недостатки
- Плохая стойкость, предсказуема, уязвима
- Ограничение 32 бита недостаточно надежное
- Недостаточный лавинный эффект на коротких строках
'''
