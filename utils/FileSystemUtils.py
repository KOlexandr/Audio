import os

__author__ = 'Olexandr'


def get_files(base_folder, extension):
    """
    find all files in base_folder and all folders inside base
    @param base_folder: start directory
    @param extension: extension of file
    @return: list of paths to files
    """
    file_paths = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths