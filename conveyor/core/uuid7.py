import time
import random



def uuid7(unix_ts_ms: int = None) -> int:

	if unix_ts_ms is None:
		unix_ts_ms = time.time_ns() // 1000000

	ver = 7
	variant = 2

	rand_a = random.getrandbits(12)
	rand_b = random.getrandbits(62)

	return (unix_ts_ms << 80) + (ver << 76) + (rand_a << 64) + (variant << 62) + rand_b