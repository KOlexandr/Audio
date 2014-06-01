import re
import sqlite3 as sql
from utils.Utils import get_files
from variables import path_to_database, path_to_examples

__author__ = 'Olexandr'


class DataBase:
    def __init__(self, path_to_db, base_audio_path, extensions=None):
        if not extensions:
            extensions = [".wav", ".flac"]
        self.con = sql.connect(path_to_db)
        self.base_audio_path = base_audio_path
        self.extensions = extensions

    def __del__(self):
        self.con.close()

    def create_lib_with_examples(self):
        """
        creates new library and adds all files from base folder as items
        @return: new Library object
        """
        for extension in self.extensions:
            paths = get_files(self.base_audio_path, extension)
            for path in paths:
                file = open(path, 'rb')
                data = file.read()
                file.close()
                self.save_file_to_database(path, data, extension.replace(".", ""))
        self.con.cursor().close()

    def save_file_to_database(self, path, data, file_type):
        sql_str = "INSERT INTO audio_files(word, file, type) VALUES(?, ?, ?)"
        self.con.cursor().execute(sql_str, [self.get_word_from_path(path), sql.Binary(data), file_type])
        self.con.commit()

    @staticmethod
    def get_word_from_path(path):
        path = re.sub("_?\\.(:?wav|flac)$", "", str(path).lower().replace("\\", "/"))
        return path[path.rfind("/")+1:]


db = DataBase(path_to_database, path_to_examples)
db.create_lib_with_examples()