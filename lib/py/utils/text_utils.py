"""Useful functions to process text files.

Author: Guangyu Peng
"""

def next_line(filepath, encoding='utf-8'):
    with open(filepath, 'r', encoding=encoding) as f:
        lines = f.readlines()
        for line in lines:
            yield line