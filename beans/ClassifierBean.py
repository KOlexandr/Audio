__author__ = 'Olexandr'


class ClassifierBean:
    def __init__(self, file_object, classified):
        self.classified = classified
        self.file_object = file_object

    def __str__(self):
        return str(self.file_object) + (" - classified" if self.classified else " - not classified")