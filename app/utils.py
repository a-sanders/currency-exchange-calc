from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def message(status, message):
    resp = {"status": status, "message": message}
    return resp


def validation_error(status, errors):
    resp = {"status": status, "errors": errors}
    return resp


def err_resp(msg, reason, code):
    resp = message(False, msg)
    resp["error_reason"] = reason
    return resp, code


def internal_err_resp():
    resp = message(False, "Something went wrong during the process!")
    resp["error_reason"] = "ERROR_SERVER_ERROR"
    return resp, 500
