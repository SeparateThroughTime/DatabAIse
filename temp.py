import itertools

taken = {0, 1, 2, 5}

iterator = (f'{i}' for i in itertools.count() if i not in taken)
name = next(iterator)
name = next(iterator)
print(name)