
def has_overlap_in_time(start1, end1, start2, end2):
    """ Check if two periods in time are overlapping or touching"""
    return (start1 >= start2 and start1 <= end2) | (end1 >= start2 and end1 <= end2)
