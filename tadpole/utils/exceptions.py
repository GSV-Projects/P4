class TadpoleException(Exception):
    pass

class TadpoleFileError(TadpoleException):
    pass

class WrongFileTypeError(TadpoleException):
    pass

class TadpoleSyntaxError(TadpoleException):
    pass

class TypecheckerException(TadpoleException):
    pass

class EvaluatorException(TadpoleException):
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column