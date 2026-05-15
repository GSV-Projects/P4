class TadpoleException(Exception):
    pass

class TadpoleFileError(TadpoleException):
    pass

class WrongFileTypeError(TadpoleException):
    pass

class TadpoleSyntaxError(TadpoleException):
    pass