from utils.PowerUtils import is_power_of_2, next_power_of_2

__author__ = 'Olexandr'


def correct_len(x, new_length=None, is_pow_of_2=False):
    """
    change size of list (make it bigger) and add zeros to needle length
    @param x: list of numbers
    @param new_length: new length of list
    @param is_pow_of_2: flag mean than length must be power of 2
    @return: list with new length and 0 in the end
    """
    if not new_length:
        new_length = len(x)
    if len(x) > new_length:
        raise Exception("New length must by bigger than current!")
    if is_pow_of_2 and not is_power_of_2(new_length):
        new_length = 2**next_power_of_2(new_length)
    return list(x) + [0]*(new_length - len(x))