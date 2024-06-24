# generate a random list with 1536 items
import random

random_list = [random.randint(0, 1535) for _ in range(1536)]
print(random_list)