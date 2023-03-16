def toreadable(num, suffix, base):
    ''' Convert a number to a human-readable string

    Args:
        num: A number
        suffix: the suffix of unit
        base: how much number should we move to another unit

    Returns:
        A string of user-friendely representation
    '''
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < base:
            return '{:g}{}{}'.format(num, unit, suffix)
        num /= base
    return '{:g}Y{}'.format(num, suffix)

def bps2readable(num):
    ''' Convert a rate (in bps) to a human-readable string

    Args:
        num: A number representing the value in bits per second

    Returns:
        A string of user-friendely representation of bps
    '''
    return toreadable(num, 'bps', 1000)

def byte2readable(num):
    ''' Convert a number (in bytes) to a human-readable string

    Args:
        num: A number representing the value in bytes

    Returns:
        A string of user-friendely representation of bytes
    '''
    return toreadable(num, 'B', 1024)
