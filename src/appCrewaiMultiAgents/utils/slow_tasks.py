import time

def test_slow_increment(x):
    time.sleep(2)
    return x + 1
