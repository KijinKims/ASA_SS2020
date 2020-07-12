import argparse

def rotation(T):
    '''
    return list of all rotations of input string
    '''
    # double the string
    TT = T + T
    ret = []
    
    # extract all substring of length with the length of T
    for i in range(len(T)):
        ret.append(TT[i:i+len(T)])
        
    return ret

def bwm(T):
    '''
    burrows-wheeler matrix
    return sorted list of rotations
    '''
    return sorted(rotation(T))

def runLengthEncoding(T):
    '''
    return run length encoding of T
    '''
    ret_str = ""
    pre_char = ""
    cnt = 0
    
    for i in range(len(T)):
        # first position
        if i == 0:
            cnt = 1
            pre_char = T[i]
        
        # if current character is changed
        elif T[i] != pre_char:
            # put the counter and corresponding character to return string
            ret_str = ret_str + str(cnt) + pre_char
            # initialize counter
            cnt = 1
            pre_char = T[i]
        # if current character is kept
        else:
            # increment the count
            cnt += 1
        # last poistion
        if i == (len(T) - 1):
            ret_str = ret_str + str(cnt) + pre_char
    
    return ret_str
    
def bwtEncoding(T):
    '''
    burrows-wheeler transform encoding
    return list of last character of each element in bwm
    '''
    return runLengthEncoding(''.join([x[-1] for x in bwm(T)]))

# referred to youtube video (https://www.youtube.com/watch?v=4n7NPk5lwbI) and its python code (https://nbviewer.jupyter.org/github/BenLangmead/comp-genomics-class/blob/master/notebooks/CG_BWT_SimpleBuild.ipynb)

def runLengthDecoding(T):
    '''
    return run length decoding of T
    '''
    cnt = ""
    ret = ""
    
    for i in range(len(T)):
        # collect number characters
        if T[i].isnumeric():
            cnt = cnt + T[i]
        # encounter character
        else:
            ret = ret + int(cnt) * T[i]
            cnt = ""
    
    return ret     

def carray(bwt):
    '''
    return C-array of bwt
    '''
    cnt_dict = {}
    
    # calculate the frequency of characters
    for char in bwt:
        if not char in cnt_dict:
            cnt_dict[char] = 1
        else:
            cnt_dict[char] += 1
    
    ret_dict = {}
    cum = 0
    
    # calculate cumulative of frequency
    for key in sorted(cnt_dict.keys()):
        ret_dict[key] = cum
        cum += cnt_dict[key]
        
    return ret_dict

def LF(bwt):
    '''
    return LF array of T
    '''

    carr = carray(bwt)
    cnt_dict = {} # count occurrence of each element 
    for key in carr.keys():
        cnt_dict[key] = 0
    
    ret_lf = []
    for i in range(len(bwt)):
        char = bwt[i]
        # calculate lf using carray and curent counter of each character
        ret_lf.append(carr[char] + cnt_dict[char])
        cnt_dict[char] += 1
    
    return ret_lf

def bwtDecoding(T):
    '''
    burrows-wheeler transform decoding
    '''
    # convert run legnth encoded form to bwt
    bwt = runLengthDecoding(T)
    
    lf = LF(bwt)
    
    # initialize return string to $ and index to 0
    ret = '$'
    curr_idx = 0
    
    while True:
        curr_char = bwt[curr_idx]
        # if encounter sentinel, finish the run
        if curr_char == '$':
            break
        
        else:
            ret = curr_char + ret
            # reset the idx using lf
            curr_idx = lf[curr_idx]
            
    return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Burrows-Wheeler Transform.')
    parser.add_argument('--encode', action='store_true')
    parser.add_argument('--decode', action='store_true')
    parser.add_argument('infile', type=argparse.FileType('r'), )
    
    args = parser.parse_args()
    if args.encode and args.decode:
        print("You must choose either encoding or decoding.")
        exit(2)
    elif not args.encode and not args.decode:
        print("You must choose either encoding or decoding.")
        exit(2)
    
    infile = args.infile
    input_lines = infile.readlines()
    infile.close()
    input_string = input_lines[0].strip()
    
    if len(input_lines) != 1:
        print("Input file should consist of one-line string.")
        exit(2)
    else:
        if args.encode:
            print(bwtEncoding(input_string))
        if args.decode:
            print(bwtDecoding(input_string))