"""Evaluator-only deterministic domain-separated pseudorandom streams."""
import hashlib
import hmac
import json


def derive(key,*parts):
    payload=json.dumps(parts,separators=(',',':'),ensure_ascii=True).encode()
    return hmac.new(key,payload,hashlib.sha256).digest()


def uniform(key,*parts):
    # 53 exact mantissa bits keep the maximum strictly below 1.0.
    return (int.from_bytes(derive(key,*parts)[:8],'big')>>11)/2**53


def bit(key,*parts):return int(uniform(key,*parts)<.5)


def integer(key,low,high,*parts):
    assert low<=high
    return low+int.from_bytes(derive(key,*parts)[:8],'big')%(high-low+1)


def opaque(key,*parts):return derive(key,*parts).hex()[:20]
