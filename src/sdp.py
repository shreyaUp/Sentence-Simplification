from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import Tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
import sys
from nltk.parse.dependencygraph import DependencyGraph


def get_children(root, tree):
    children = []
    for key in tree.keys():
        if tree[key]['root'] == root and tree[key]['pos'][0] != 'V':
            children.append(tree[key]['index'])
    return children

#######################################################################################

def create_dict(tree):
    dict_list = dict()
    dep_tree = dict()
    dict_list[0] = {'index':0,'word':'///root','root':None}
    for line in tree:
        print("line: ",line)
        if len(line) < 2:
            continue
        d_temp = {'index':int(line[0]),
                'word':line[1],
                'rootword':line[2],
                'cpos':line[3],
                'pos':line[4],
                'tam':line[5],
                'root':int(line[6]),
                'rel':line[7],
                'rootrel':line[8],
                'other':line[9]}
        dict_list[d_temp['index']] = d_temp
        dep_tree[d_temp['index']] = d_temp['root']
    return dict_list, dep_tree

##########################################################################################

def find_all_deps(triple, triples):
    word1, rel, word2 = triple
    dep = []
    for t in triples:
        w1, r, w2 = t
        # print("triple in fn: ",w1, w2, r)
        if w1 == word1 or w2 == word1:
            if r != 'nsubj' and r != 'nsubjpass':
                # print("triple added: ",w1, w2, r)
                dep.append(t)
    for t in triples:
        w1, r, w2 = t
        if w1 == word2 or w2 == word2:
            if r != 'nsubj' and r != 'nsubjpass':
                # print("triple added: ",w1, w2, r)
                dep.append(t)
    # print("-----------------------------------------------------------------")
    # print(dep)
    # print("-----------------------------------------------------------------")
    return dep

###########################################################################################

def cmp(a, b):
    return (a > b) - (a < b)

#############################################################################################

def format(jar_location):

    path_to_jar = jar_location + '/stanford-parser.jar'
    path_to_models_jar = jar_location + '/stanford-parser-3.9.2-models.jar'
    sentence = input("Enter a sentence : ")
    dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
    tokens = word_tokenize(sentence)
    print(" ======== TOKENS =======")
    print(tokens)
    result = dependency_parser.raw_parse(sentence)
    print("\n")
    

    for dep in result:
        cf = CanvasFrame()
        t = dep.tree()
        tc = TreeWidget(cf.canvas(),t)
        cf.add_widget(tc,10,10)
        cf.print_to_file('tree.ps')
        cf.destroy()
    triples = dep.triples()
    
    
    parsed_tree = dep.to_conll(10)
    lines = []
    line = []
    print(parsed_tree)
    tree = parsed_tree.split("\n")
    for i in range(0,len(tree)):
        line = tree[i].split("\t")
        lines.append(line)

    lines = [line for line in lines if len(line) == 10]
    verbs = {}
    print("=========  Verbs in Sentence ==========")   
    for line in lines:
        if line[3][0] == "V":
            print(" Word : ", line[1])
            print(" Tag: ", line[3])
            verbs[int(line[0])] = line[3]
    
    if(len(verbs) >= 2):
        print("Sentence : \"",sentence, "\" is complex!")
    else:
        print("Sentence : ",sentence, " is simple!")
        exit()
    print("=======================================\n")
    
    dict_tree, dep_tree = create_dict(lines)

    word_dep = {}
    # Find all the dependencies of the verbs
    for i in range(0,int(lines[-1][0])+1):
        word_dep[i] = get_children(i, dict_tree)
    
    print("============== Word Dependencies =============")
    print(word_dep)

    # for verb in verbs.keys():
    #     if len(word_dep[verb]) > 0:
    #         child_nodes = word_dep[verb]
    #     else:
    #         continue
    #     new_children = []
    #     for child in child_nodes:
    #         new_children.extend(word_dep[child])
    #     word_dep[verb].extend(new_children)

    # for verb in verbs.keys():
    #     word_dep[verb] = sorted(word_dep[verb])
    #     print(word_dep[verb])
    #     print("-------------------------------------")
    
    # verb_index = list(verbs.keys())
    # for i in range(0,len(verb_index)):
    #     for j in range(i+1, len(verb_index)):
    #         if lines[j][4][0] != 'V':
    #             print(" POS TAG: ",lines[j][4])
    #             word_dep[verb_index[i]] = list(set(word_dep[verb_index[i]]) - set(word_dep[verb_index[j]]))
    
    # for verb in verbs.keys():
    #     print(word_dep[verb])
    #     print("-------------------------------------")
    
    clause_start = []
    triples_list = []
    print("=============== TRIPLES =============")
    for triple in triples:
        w1, rel, w2 = triple
        print(rel, w1, w2)
        if rel == 'nsubj' or rel== 'nsubjpass':
            clause_start.append(triple)
        triples_list.append(triple)

    print("\n\n\n")

    clause_words = {}
    for clause in clause_start:
        w1, rel, w2 = clause
        print("Clause : ",clause)
        clause_words[clause] = []
        for triple in triples_list:
            word1, reln, word2 = triple
            # print("Triple for Clause: ", reln, word1, word2)
            if cmp(triple, clause) == False:
                if word1 == w1 or word1 == w2 and ( reln != 'nsubj' and reln != 'nsubjpass' ):
                    clause_words[clause].append(triple)
                    clause_words[clause].extend(find_all_deps(triple, triples_list))
                elif word2 == w1 or word2 == w2 and ( reln != 'nsubj' and reln != 'nsubjpass' ):
                    clause_words[clause].append(triple)
                    clause_words[clause].extend(find_all_deps(triple, triples_list,[]))

    # for clause in clause_words:
    #     clause_list = clause_words[clause]
    #     for i in range(0,len(clause_list)):
    #         print("Dep: ",dep)
    #         dep_list = find_all_deps(tuple(clause_list[i]), triples_list)
    #         for dep in dep_list:
    #             if dep not in clause_list:
    #                 clause_list.append(dep)
                
    print("\n\n============= Clause Boundary ==============")
    for clause in clause_words:
        print("Clause: ",clause)
        words = []
        for clause_list in clause_words[clause]:
            w1, rel, w2 = clause_list
            words.append(w1[0])
            words.append(w2[0])
        words = set(words)
        word_ind = []
        for i in range(len(tokens)):
            if tokens[i] in words:
                word_ind.append(i)
        print(sorted(word_ind))
        word_ind = sorted(word_ind)
        add_list = []
        for w in word_ind:
            word_ind.extend(list(word_dep[w]))
        word_ind = sorted(set(word_ind))
        print(word_ind)
        print("=======================================")

format(sys.argv[1]) 
