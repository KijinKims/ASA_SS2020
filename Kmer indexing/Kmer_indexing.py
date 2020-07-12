import sys
import os.path

def kmer_indexing(main_text, k):
    kmer_index = {}

    for i in range(0, len(main_text) - k + 1):
        kmer = main_text[i:i + k]
        if kmer not in kmer_index.keys():
            kmer_index[kmer] = [i]
        else:
            kmer_index[kmer].append(i)

    return kmer_index

def index_dict_to_string(index_dict):

    ret = ""

    for key in sorted(index_dict.keys()):
        ret += key + " " + ','.join([str(x) for x in index_dict[key]]) + '\n'
    return ret

def kmer_query(index_dict, query):

    if query in index_dict.keys():
        return ','.join([str(x) for x in index_dict[query]])
    else:
        return '-1'

def is_intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# argument parsing
main_text = sys.argv[1]
k = sys.argv[2]
queries_text = sys.argv[3]

# sanity check
assert os.path.isfile(main_text), "main text file does not exist."
assert is_intstring(k), "k is not integer."
assert os.path.isfile(queries_text), "queries file does not exist."

# variable setting
k = int(k)
main_text_f = open(main_text, "r")
queries_f = open(queries_text, "r")
output_kmer_indicies = open("kmer_indices.txt", "w")
output_queries_indices = open("queries_indices.txt", "w")

# main text parsing
line = main_text_f.readline()
main_sequence = line.strip()
main_text_f.close()

# sanity check
for i in main_sequence:
    assert i in ['A','T','G','C'], "Sequence should consist of A,T,G and C. Your sequence has " + i + "."

# queries text parsing
lines = queries_f.readlines()
queries = []
for line in lines:
    query = line.strip()
    for i in query:
        assert i in ['A', 'T', 'G', 'C'], "Queries should consist of A,T,G and C. Your query has " + i + "."
    queries.append(query)
queries_f.close()

# 'main_sequence' is main sequence string, 'k' is k and 'queries' is a list of query
index_dict = kmer_indexing(main_sequence, k)
index_dict_str = index_dict_to_string(index_dict)

queries_result_str = ""
for query in queries:
    queries_result_str += query + " " + kmer_query(index_dict, query) +"\n"

# export the result
output_kmer_indicies.write(index_dict_str)
output_queries_indices.write(queries_result_str)

output_kmer_indicies.close()
output_queries_indices.close()