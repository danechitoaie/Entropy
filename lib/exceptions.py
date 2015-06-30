class EntropyException(Exception):
    pass

class EntropyHttpUnauthorizedException(EntropyException):
    pass

class EntropyHttpMkcolException(EntropyException):
    pass

class EntropyHttpPropFindException(EntropyException):
    pass

class EntropyHttpNoContentException(EntropyException):
    pass

class EntropyHttpPutException(EntropyException):
    pass

class EntropyVerifyCodeDirectoryException(EntropyException):
    pass
