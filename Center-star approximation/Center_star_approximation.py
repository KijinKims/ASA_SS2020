import sys

def edit_dist(s1, s2, mismatch_cost=1, ins_cost=1, del_cost=1):
    '''
    calculate the edit distance between two sequences using Needleman–Wunsch algorithm
    '''
    def similarity_score(x, y):
        if x == y:
            return 0
        else:
            return mismatch_cost

    n = len(s1)
    m = len(s2)

    H = [[0 for i in range(m + 1)] for i in range(n + 1)] # scoring matrix
    T = [[0 for i in range(m + 1)] for i in range(n + 1)] # backtrack matrix

    # initialize the first row and column with incrementing number
    for i in range(1, n + 1):
        H[0][i] = i
        H[i][0] = i

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            deletion = (H[i - 1][j] + del_cost, 1)
            insertion = (H[i][j - 1] + ins_cost, 2)
            match = (H[i - 1][j - 1] + similarity_score(s1[i - 1], s2[j - 1]), 3)
            # keep track of the predecessor of each cell with backtrack matrix
            H[i][j], T[i][j] = min(
                deletion,
                insertion,
                match
            )

    def backtrack(B):
        '''
        backtrack using backtrack matrix
        reference: https://stackoverflow.com/questions/12666494/how-do-i-decide-which-way-to-backtrack-in-the-smith-waterman-algorithm
        '''
        i = n
        j = m

        while B[i][j] > 0:
            if B[i][j] == 3:
                i -= 1
                j -= 1
                yield s1[i], s2[j]
            elif B[i][j] == 2:
                j -= 1
                yield '-', s2[j]
            elif B[i][j] == 1:
                i -= 1
                yield s1[i], '-'

        while i > 0:
            i -= 1
            yield s1[i], '-'

        while j > 0:
            j -= 1
            yield '-', s2[j]

    def backtrack_to_align():
        '''
        get yields from backtrack() and make it into alignment form
        '''
        ret_align = []
        aligned_a = []
        aligned_b = []

        for i, j in backtrack(T):
            aligned_a.append(i)
            aligned_b.append(j)

        ret_align.append(''.join(reversed(aligned_a)))
        ret_align.append(''.join(reversed(aligned_b)))

        return ret_align

    return H[n][m], backtrack_to_align()


def collapse_alns(aln1, aln2):
    '''
    collapse two alignments using the center sequences as pivot
    reference https://www.site.uottawa.ca/~lucia/courses/5126-11/lecturenotes/12-13MultipleAlignment.pdf
    '''
    # center sequences in possibly different alignment forms
    center1 = aln1[0]
    center2 = aln2[0]

    # sequences other than center sequence
    rest1 = aln1[1:]
    rest2 = aln2[1:]

    # new center sequence to have merged alignment from two alignments
    new_center = center1

    i = 0
    j = 0

    # until one of center sequence reach end
    while i < len(center1) and j < len(center2):
        # both center sequences have gap on index i
        if center1[i] == '-' and center2[j] == '-':
            i += 1
            j += 1
        # both center1 have gap on index i
        elif center1[i] == '-' and center2[j] != '-':
            # gap inserted into index i of rest sequence in pair with center2
            rest2 = [x[0:j] + '-' + x[j:] for x in rest2]
            i += 1
        elif center1[i] != '-' and center2[j] == '-':
            # gap inserted into index i of rest sequence in pair with center1
            rest1 = [x[0:i] + '-' + x[i:] for x in rest1]
            # gap inserted into index i of new center
            new_center = new_center[0:i] + '-' + new_center[i:]
            j += 1
        else:
            # this case(neither has gap on i and characters from each are different) should not happen
            if center1[i] != center2[j]:
                print("something wrong")
                exit(2)
            # neither has gap on i and characters are same
            else:
                i += 1
                j += 1

    # until remaining i is used up, put gap on every sequences of rest2
    while i < len(center1):
        rest2 = [x + '-' for x in rest2]
        i += 1

    # until remaining j is used up, put gap on every sequences of rest1 and new center sequence
    while j < len(center2):
        rest1 = [x + '-' for x in rest1]
        new_center = new_center + '-'
        j += 1

    # return collapsed alignments having new center sequence at front
    return [new_center] + rest1 + rest2


if __name__ == '__main__':

    input_f = open(sys.argv[1], "r")
    input_lines = input_f.readlines()
    output_f = open(sys.argv[2], "w")

    input_names = []
    input_sequences = []

    for line in input_lines:

        # save name of each sequences for final output
        if line.startswith(">"):
            input_names.append(line.strip())
        else:
            input_sequences.append(line.strip())

    n = len(input_sequences)

    # pair-wise distance matrix
    dist_matrix = [[0 for i in range(n)] for i in range(n)]
    # pair-wise alignment matrix
    aln_matrix = [["" for i in range(n)] for i in range(n)]

    for i in range(n):
        for j in range(i, n):
            # zero distance between sequence and itself
            if i == j:
                dist_matrix[i][j] = 0
            else:
                # fill out pair-wise distance and alignment matrix
                calculated_dist, aln = edit_dist(input_sequences[i], input_sequences[j])
                dist_matrix[i][j] = dist_matrix[j][i] = calculated_dist
                aln_matrix[i][j] = aln
                # this step for placing center sequence at 0-index always
                aln_matrix[j][i] = aln[::-1]

    min_seq_idx = 0
    min_overall_dist = float('inf')
    over_all_dist = []
    # find center sequence with minimum overall distance
    for i in range(n):
        sum = 0

        for j in range(n):
            sum += dist_matrix[i][j]

        if sum < min_overall_dist:
            min_overall_dist = sum
            min_seq_idx = i
        over_all_dist.append(sum)

    # print each overall distance
    print(','.join([str(x) for x in over_all_dist]))

    # list of alignments having center sequence as first element, also not having alignment with itself
    alns = []
    for i in [i for i in range(n) if i != min_seq_idx]:
        alns.append(aln_matrix[min_seq_idx][i])

    # collapse alignments
    tmp = collapse_alns(alns[0], alns[1])
    for i in range(2,len(alns)):
        tmp = collapse_alns(tmp, alns[i])

    # after collapsing, center sequence is at first, so relocate it at its original position
    result = tmp[1:]
    result = result[:min_seq_idx] + [tmp[0]] + result[min_seq_idx:]

    # write outputs
    for i in range(len(input_names)):
        output_f.write(input_names[i]+'\n')
        output_f.write(result[i]+'\n')