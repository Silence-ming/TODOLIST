import hashlib
def md5(str):
    md5=hashlib.md5()
    md5.update(str.encode('utf8'))
    return md5.hexdigest()