import subprocess
from abc import ABCMeta, abstractmethod


class Language(metaclass=ABCMeta):
    @abstractmethod
    def run(self, code: bytes, input_data: bytes):
        pass


class Python(Language):
    def run(self, code: bytes, input_data: bytes) -> bytes:
        try:
            output = subprocess.check_output(['python3.10', '-c', code.decode()], input=input_data)
        except subprocess.CalledProcessError:
            return None
        else:
            return output


class LanguageFactory:
    def get_language(self, language):
        if language == 'python':
            return Python()
        else:
            return None
