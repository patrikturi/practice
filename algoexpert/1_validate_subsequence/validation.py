from typing import Sequence


def isValidSubsequence(array: Sequence[int], sequence: Sequence[int]) -> bool:
    array_index = 0
    last_matching_sequence_index = -1
    for i, s in enumerate(sequence):
        while array_index < len(array):
            a = array[array_index]
            array_index += 1
            if a == s:
                last_matching_sequence_index = i
                break

    return last_matching_sequence_index == len(sequence) - 1


def isValidSubsequence2(array: Sequence[int], sequence: Sequence[int]) -> bool:
    matching_items = []
    array_index = 0
    for s in sequence:
        while array_index < len(array):
            a = array[array_index]
            array_index += 1
            if a == s:
                matching_items.append(a)
                break

    return matching_items == sequence


def isValidSubsequence3(array: Sequence[int], sequence: Sequence[int]) -> bool:
    search_start_position = 0
    for s in sequence:
        try:
            search_start_position = array.index(s, search_start_position) + 1
        except ValueError:
            return False

    return True
