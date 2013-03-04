import re

def natsort(string_):
    """Natural sort. Usage: sorted(list, key=natural_sort)"""
    #http://stackoverflow.com/questions/2545532/python-analog-of-natsort-function-sort-a-list-using-a-natural-order-algorithm
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
