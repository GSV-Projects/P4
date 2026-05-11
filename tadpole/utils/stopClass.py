# Custom exception for stop, it's only purpose is to be caught, so the exception itself doesn't do anything
class stop(Exception):
    pass