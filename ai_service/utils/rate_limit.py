from functools import wraps
from flask import jsonify

rate_table = {}

def rate_limit(ip, limit=5):
    if ip not in rate_table:
        rate_table[ip] = 1
    else:
        rate_table[ip] += 1
    
    return rate_table[ip] <= limit
