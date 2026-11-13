class CustomException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class Error(CustomException):
    def __init__(self, message: str) -> None:
        """
        These ones crash the program
        """
        message_start: str = "[ERROR]: "
        formatted_message: str = f"{message_start}{message}"
        super().__init__(formatted_message)

