from enum import Enum


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH ERROR'
    PARSING_ERROR = 'PARSING ERROR'
