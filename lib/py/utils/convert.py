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

def tounit(num, target, base):
    ''' Convert a number by a target unit

    Args:
        num: A number
        target: target unit, eg. 'K' 'M' 'G'
        base: how much number should we move to another unit

    Returns:
        A number with target unit

    Example:
        tounit(1000, 'K', 1000) returns 1.0
    '''
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if unit == target:
            return num
        num /= base
    return num

def bps2Kbps(num):
    ''' Convert a rate (in bps) to a rate (in Kbps) '''
    return tounit(num, 'K', 1000)

def bps2Mbps(num):
    ''' Convert a rate (in bps) to a rate (in Mbps) '''
    return tounit(num, 'M', 1000)

def bps2Gbps(num):
    ''' Convert a rate (in bps) to a rate (in Gbps) '''
    return tounit(num, 'G', 1000)

def bps2Tbps(num):
    ''' Convert a rate (in bps) to a rate (in Tbps) '''
    return tounit(num, 'T', 1000)

def byte2KB(num):
    ''' Convert a number (in bytes) to a number (in KB) '''
    return tounit(num, 'K', 1024)

def byte2MB(num):
    ''' Convert a number (in bytes) to a number (in MB) '''
    return tounit(num, 'M', 1024)

def byte2GB(num):
    ''' Convert a number (in bytes) to a number (in GB) '''
    return tounit(num, 'G', 1024)

def byte2TB(num):
    ''' Convert a number (in bytes) to a number (in TB) '''
    return tounit(num, 'T', 1024)