
@public
def copymerge(dictin, newvals):
    result = dictin.copy()
    result.update(newvals)
    return result
