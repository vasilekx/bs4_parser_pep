from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'


DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_DIR_NAME = 'logs'
LOG_FILE_NAME = 'parser.log'
RESULTS_DIR_NAME = 'results'
PRETTY_ARGUMENT_NAME = 'pretty'
FILE_ARGUMENT_NAME = 'file'


BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / LOG_DIR_NAME
LOG_FILE = LOG_DIR / LOG_FILE_NAME
RESULTS_DIR = BASE_DIR / RESULTS_DIR_NAME


EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}
