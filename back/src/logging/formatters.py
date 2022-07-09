import logging
import colorama
import databases


class DataBaseFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        result = list(map(lambda e: ', '.join(list(map(lambda x: str(x), list(e.values())))), record.result)) \
            if isinstance(record.result, list) else str(list(record.result.values()))

        record.result = result
        record.levelname = colorama.Fore.GREEN + record.levelname + colorama.Fore.RESET
        record.sql = colorama.Fore.BLUE + record.sql + colorama.Fore.RESET
        return super(DataBaseFormatter, self).format(record)
