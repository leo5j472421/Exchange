import time,json,logging
from function import *


def reserve(s):
    pair = s.split('_')
    return '{}_{}'.format(pair[1],pair[0])
