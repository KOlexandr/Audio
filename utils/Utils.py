__author__ = 'Olexandr'


def get_all_waves(files_list):
    """
    get all files from list and create list of WavFile objects
    @param files_list: list of paths to files
    @return: list of WavFile objects
    """
    waves = []
    for i in files_list:
        waves.append(WavFile(i))
    return waves