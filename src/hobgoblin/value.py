def firstof(*args):
    for x in args:
        if x is not None:
            return x
    raise Exception("No valid values")
