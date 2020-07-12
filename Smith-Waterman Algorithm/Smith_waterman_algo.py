import sys

def smith_waterman(a, b, match_cost, mismatch_cost, gap_cost):
    def similarity_score(x, y):
        if x == y:
            return match_cost
        else:
            return mismatch_cost

    n = len(a)
    m = len(b)

    best, besti, bestj = 0, [], []

    H = [[0 for i in range(m + 1)] for i in range(n + 1)]
    T = [[0 for i in range(m + 1)] for i in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            deletion = (H[i - 1][j] + gap_cost, 0)
            insertion = (H[i][j - 1] + gap_cost, 1)
            match = (H[i - 1][j - 1] + similarity_score(a[i - 1], b[j - 1]), 2)
            H[i][j], T[i][j] = max(
                (0, 0),
                deletion,
                insertion,
                match
            )

            if H[i][j] > best:
                best = H[i][j]
                besti = [i]
                bestj = [j]
            elif H[i][j] == best:
                besti.append(i)
                bestj.append(j)
            else:
                pass

    if best == 0:
        besti, bestj = [], []

    def dp_table(H):
        def split(word):
            return [char for char in word]

        table = [["" for i in range(m + 2)] for i in range(n + 2)]

        table[0] = [" ", " "] + split(b)

        split_a = [" "] + split(a)
        for i in range(1, n + 2):
            table[i] = [split_a[i - 1]] + [str(x) for x in H[i - 1]]

        def to_string(table):
            ret = ""
            for i in range(len(table)):
                ret = ret + " ".join(table[i]) + "\n"
            return ret

        return to_string(table)

    def backtrack(B):
        while besti:
            i = besti.pop()
            j = bestj.pop()

            while H[i][j] > 0:
                if B[i][j] == 2:
                    i -= 1
                    j -= 1
                    yield (a[i], b[j])
                elif B[i][j] == 1:
                    j -= 1
                    yield ('_', b[j])
                elif B[i][j] == 0:
                    i -= 1
                    yield (a[i], '_')
            yield ("pos", str(j))

    def backtrack_to_align():
        ret_align = ""
        aligned_a = []
        aligned_b = []

        for i, j in backtrack(T):
            if i == "pos":
                ret_align += i + " " + j + "\n"
                if aligned_a:
                    ret_align += ''.join(reversed(aligned_a)) + "\n"
                    ret_align += ''.join(reversed(aligned_b)) + "\n"
                    aligned_a = []
                    aligned_b = []

            else:
                aligned_a.append(i)
                aligned_b.append(j)

        return ret_align

    return dp_table(H), backtrack_to_align()

def is_intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

first_string = sys.argv[1]
second_string = sys.argv[2]
match_cost = sys.argv[3]
mismatch_cost = sys.argv[4]
gap_cost = sys.argv[5]

assert isinstance(first_string, str), "first_string is not string."
assert isinstance(second_string, str), "second_string is not string."
assert is_intstring(match_cost), "match_cost is not integer."
assert is_intstring(mismatch_cost), "mismatch_cost is not integer."
assert is_intstring(gap_cost), "gap_cost is not integer."

match_cost = int(match_cost)
mismatch_cost = int(mismatch_cost)
gap_cost = int(gap_cost)

for i in first_string:
    assert i in ['A','T','G','C'], "Strings should consist of A,T,G and C. Your string has " + i + "."
for i in second_string:
    assert i in ['A','T','G','C'], "Strings should consist of A,T,G and C. Your string has " + i + "."

if match_cost < mismatch_cost or match_cost < gap_cost:
    print("Generally, match cost is bigger than mismatch cost and gap cost. Are you sure with these costs?")

output_dp_table = open("dp_table.txt", "w")
output_alignment = open("alignment.txt", "w")

dp_table, alignment = smith_waterman(first_string, second_string, match_cost, mismatch_cost, gap_cost)

if not alignment:
    output_alignment.write("No valid alignment")

output_dp_table.write(dp_table)
output_alignment.write(alignment)

output_dp_table.close()
output_alignment.close()