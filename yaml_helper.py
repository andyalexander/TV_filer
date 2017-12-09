def yaml_get(y, key):
    if key in y:
        return y[key]
    else:
        return None