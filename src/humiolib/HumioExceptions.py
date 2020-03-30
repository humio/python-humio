class HumioException(Exception):
   pass

class HumioConnectionException(HumioException):
   pass

class HumioHTTPException(HumioException):
   def __init__(self, message, status_code=None):
      self.message = message
      self.status_code = status_code

class HumioTimeoutException(HumioException):
   pass

class HumioConnectionDroppedException(HumioException):
   pass

class HumioQueryJobExhaustedException(HumioException):
   pass

class HumioQueryJobExpiredException(HumioException):
   pass