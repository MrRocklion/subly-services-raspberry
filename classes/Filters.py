# filters.py
import logging

class ExcludePathsFilter(logging.Filter):
    def __init__(self, excluded_paths):
        super().__init__()
        self.excluded_paths = excluded_paths

    def filter(self, record):
        # Werkzeug logs suelen tener la ruta en el mensaje como "GET /ruta HTTP/1.1"
        if any(path in record.getMessage() for path in self.excluded_paths):
            return False
        return True
