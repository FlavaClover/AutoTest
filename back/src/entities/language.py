import hashlib
import subprocess
import uuid
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


class Cpp(Language):
    def run(self, code: bytes, input_data: bytes):
        try:
            filename_cpp = str(uuid.uuid4()) + '.cpp'
            filename_o = filename_cpp.strip('.cpp') + '.o'
            with open(filename_cpp, 'wb') as cpp:
                cpp.write(code)

            subprocess.run(['g++', filename_cpp, '-o', filename_o])
            output = subprocess.check_output(['./' + filename_o], input=input_data)
            subprocess.run(['rm', filename_cpp])
            subprocess.run(['rm', filename_o])

        except subprocess.CalledProcessError:
            return None
        else:
            return output


class LanguageFactory:
    def get_language(self, language):
        if language == 'python':
            return Python()
        elif language == 'cpp':
            return Cpp()
        else:
            return None
