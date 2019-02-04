# DragAndDropRank calculations
#
# Convert alphanumeric string in Rally to numeric value
#
# Based on https://comm.support.ca.com/kb/interpret-draganddroprank/kb000047752

CHAR_LIST = ['!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{','|','}','~']

def _calculateNumber(item, pos):
    index = CHAR_LIST.index(item)
    result = (index * (94**pos))
    return(result)

def calculateRank(inputString, charCount):
    # Get the first charCount characters and reverse the string
    revStr = inputString[:charCount][::-1]
    ctr = 0
    total = 0
    for i in revStr:
        total += _calculateNumber(i, ctr)
        ctr += 1
    return(total)

def test():
    '''Verify functionality'''
    dndRank1 = 'P!!$*'
    dndRank1_numeric = 3669520403
    dndRank2 = 'P!!$)'
    dndRank2_numeric = 3669520402
    dndRank3 = 'P!!$('
    dndRank3_numeric = 3669520401

    print("calculateRank(" + dndRank1 + ") = " + str(calculateRank(dndRank1, 5)) + "; matches? " + str(dndRank1_numeric == calculateRank(dndRank1, 5)))
    print("calculateRank(" + dndRank2 + ") = " + str(calculateRank(dndRank2, 5)) + "; matches? " + str(dndRank2_numeric == calculateRank(dndRank2, 5)))
    print("calculateRank(" + dndRank3 + ") = " + str(calculateRank(dndRank3, 5)) + "; matches? " + str(dndRank3_numeric == calculateRank(dndRank3, 5)))
