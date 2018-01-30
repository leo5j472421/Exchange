import time, logging,function


def reserve(s):  # BTC-1ST to 1ST_BTC
    s = s.split('-')
    return s[1] + '_' + s[0]


def reserve2(s):  # 1ST_BTC to BTC-1ST
    s = s.split('_')
    return s[1] + '-' + s[0]
