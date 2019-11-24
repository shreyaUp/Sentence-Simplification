import nltk
import parse

def get_index(dict1, tree, word_1, word_2):
    l = []
    for k, v in dict1.items():
        if v == word_1[0] and word_1 in tree[word_2]:
            l.append(k)
    if l == []:
        return 100000
    return l[0]

###################################################################################

def get_sentence_dict():
    clause_dict= {}
    with open('./clause_output.txt', 'r') as out_f:
        for line in out_f.readlines():
            if line.split(':')[0] == 'Input Sentence':
                sentence = line.split(':')[1].split('\"')[0].strip()
            elif 'Clause' in line.split(':')[0]:
                key = line.split(':')[0].strip()[6]
                value = line.split(':')[1].strip()
                clause_dict[key] = value
    return sentence, clause_dict

#####################################################################################

def find_clause_breakpoints(clause_marked, tree, sentence_dict):
    clause_breakpoint = {}
    for k, v in clause_marked.items():
        word_1,relation,word_2 = v
        nearest_noun_index = 100000
        if word_2 not in tree:
            continue
        for w, crel in tree[word_2].items():
            if w[1][0] == 'N' or crel == 'nsubj' or crel == 'expl' or crel == 'advmod':
                temp = min(get_index(sentence_dict, tree, w, word_2),get_index(sentence_dict, tree, w, word_2))
                if temp < nearest_noun_index:
                    nearest_noun_index = temp

        if nearest_noun_index == 100000:
            continue
        clause_breakpoint[v] = (nearest_noun_index, sentence_dict[nearest_noun_index])
    return clause_breakpoint

################################################################################################

def complete_sentence():
    clause_dict = dict()
    sentence = str()
    clause_marked = {}
    tree = {}
    clause_relations = ['parataxis','ccomp','acl','acl:relcl','advcl','conj']

    sentence, clause_dict = get_sentence_dict()
    print("Test Sentence---->", sentence)

    sentence_dict = {k:v for k, v in enumerate(sentence.split( ))}
    parsed, tokens = parse.format(sentence)
    input_tree = parsed.to_conll(4)

    # Getting the POS Tags for all the words in the sentences
    pos_tags = [line.split('\t')[1] for line in input_tree.split('\n') if line != '' and line.split('\t')[1] != 'POS']
    print(" ============= POS TAGS =============")
    print(pos_tags)

    #Converting parsed sentence to triples (w1, relation, w2)
    triples = parsed.triples()
    conll = parsed.to_conll(10)
    dot = parsed.to_dot()
    
    for p in triples:
        print("======= Triple ===========")
        print(p)
        word_1, relation, word_2 = p
        if word_1 not in tree:
            tree[word_1] = {}
        if word_2 not in tree[word_1]:
            tree[word_1][word_2] = relation
        if relation in clause_relations:
            clause_marked[relation] = p
    print(clause_marked)
    
    # print("=========== TREE ==========")
    # for key in tree:
    #     print(key, tree[k])
    # print("\n\n")
    
    clause_breakpoint = find_clause_breakpoints(clause_marked, tree, sentence_dict)
    print("======= Clause Breakpoints =======")
    print(clause_breakpoint)

    break_point = [v[0] for v in clause_breakpoint.values()]
    break_point = sorted(break_point)
    xc = 1
    # print(" break_point: ",break_point)
    Sentences = {}
    for k, v in sorted(sentence_dict.items(),key = lambda x : x[0]):
        print(" in For Loop : k and v : ", k,v)
        if k == break_point[0]:
            xc += 1
        if pos_tags[k] == 'CC' or pos_tags[k] == 'WRB' or pos_tags[k] == 'WDT':
            continue

        stored_p = ()
        stored_l = []
        # print(v)
        for key in clause_breakpoint:
            print(v, key[2][0], key[1])
            if v == key[2][0] and key[1] == 'acl:relcl':
                stored_p = key[0]
        # print("stored p: ",stored_p)
        if stored_p != ():
            for asd in tree[stored_p]:
                # print(asd)
                if asd[0] != v:
                    # print(asd)
                    stored_l.append(asd[0])
            # print(stored_l)
            stored_l.append(stored_p[0])
            v += ' '+ ' '.join(stored_l)
        cn = 'Clause'+str(xc)
        # print("CN: ",cn)
        if cn not in Sentences:
            Sentences[cn] = ''
            v = v.capitalize()
        Sentences[cn] += v + ' '
    for k, v in Sentences.items():
        print(k,": ",v.strip())

complete_sentence()