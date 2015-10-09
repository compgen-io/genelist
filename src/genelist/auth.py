# authentication methods
import os
import hashlib
import binascii
from struct import pack

try:
    from genelist import conf
except:
    pass


def authenticate(username, password):
    found_pass = None
    with conf.conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM users WHERE username = %s', (username,))
        record = cur.fetchone()
        cur.close()

    if not record:
        return False

    userid = record[0]
    found_pass = record[1]

    method, val = found_pass.split("$", 1)

    if method == 'pbkdf2':
        salt, hashed_passwd = val.split('$', 1)

        # PBDKF2_HMAC, using the embedded salt
        dk = backported_pbkdf2_hmac('sha256', password, salt, 100000)
        if secure_compare(hashed_passwd, binascii.hexlify(dk)):
            return userid

    return None


def generate_salt(n=16):
    rand_string = os.urandom(n)
    return binascii.hexlify(rand_string)


def secure_compare(foo, bar):
    match = True
    for one, two in zip(foo, bar):
        if one != two:
            match = False

    return match


####################################################################
#    BACKPORTED From:  Python 2.7.8
#    See: https://pypi.python.org/pypi/backports.pbkdf2/0.1
####################################################################


_string_type = basestring
_trans_5C = b''.join(chr(x ^ 0x5C) for x in xrange(256))
_trans_36 = b''.join(chr(x ^ 0x36) for x in xrange(256))


def _loop_counter(loop, pack=pack):
    return pack(b'>I', loop)


# hack from django.utils.crypto
def _from_bytes(value, endianess, int=int):
    return int(binascii.hexlify(value), 16)


def _to_bytes(value, length, endianess):
    fmt = '%%0%ix' % (2 * length)
    return binascii.unhexlify(fmt % value)


def backported_pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
    """
    Password based key derivation function 2 (PKCS #5 v2.0)

    This Python implementations based on the hmac module about as fast
    as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
    for long passwords.

    Timings in seconds for pbkdf2_hmac('sha256', b'password10', b'salt', 50000)
    on an Intel I7 with 2.50 GHz:

    len(password)  Python 3.3  OpenSSL 1.0.1e  OpenSSL patched
    -------------  ----------  --------------  ---------------
    10             0.408       0.431           0.233
    100            0.418       0.509           0.228
    500            0.433       1.01            0.230
    1000           0.435       1.61            0.228
    -------------  ----------  --------------  ---------------

    On Python 2.7 the code runs about 50% slower than on Python 3.3.
    """
    if not isinstance(hash_name, _string_type):
        raise TypeError(hash_name)

    # no unicode, memoryview and other bytes-like objects are too hard to
    # support on 2.6 to 3.4
    if not isinstance(password, (bytes, bytearray)):
        password = memoryview(str(password)).tobytes()
    if not isinstance(salt, (bytes, bytearray)):
        salt = memoryview(str(salt)).tobytes()

    # Fast inline HMAC implementation
    inner = hashlib.new(hash_name)
    outer = hashlib.new(hash_name)
    blocksize = getattr(inner, 'block_size', 64)
    if len(password) > blocksize:
        password = hashlib.new(hash_name, password).digest()
    password = password + b'\x00' * (blocksize - len(password))
    inner.update(password.translate(_trans_36))
    outer.update(password.translate(_trans_5C))

    def prf(msg, inner=inner, outer=outer):
        # PBKDF2_HMAC uses the password as key. We can re-use the same
        # digest objects and and just update copies to skip initialization.
        icpy = inner.copy()
        ocpy = outer.copy()
        icpy.update(msg)
        ocpy.update(icpy.digest())
        return ocpy.digest()

    if iterations < 1:
        raise ValueError(iterations)
    if dklen is None:
        dklen = outer.digest_size
    if dklen < 1:
        raise ValueError(dklen)

    from_bytes = _from_bytes
    to_bytes = _to_bytes
    loop_counter = _loop_counter

    dkey = b''
    loop = 1
    while len(dkey) < dklen:
        prev = prf(salt + loop_counter(loop))
        # endianess doesn't matter here as long to / from use the same
        rkey = from_bytes(prev, 'big')
        for i in range(iterations - 1):
            prev = prf(prev)
            # rkey = rkey ^ prev
            rkey ^= from_bytes(prev, 'big')
        loop += 1
        dkey += to_bytes(rkey, inner.digest_size, 'big')

    return dkey[:dklen]


if __name__ == '__main__':
    import sys
    print "Username     : %s" % sys.argv[1]
    salt = generate_salt() if len(sys.argv) < 3 else sys.argv[3]
    print "Password hash: 1;%s;%s" % (salt, binascii.hexlify(backported_pbkdf2_hmac('sha256', sys.argv[2], salt, 100000)))
