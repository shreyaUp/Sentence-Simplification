import sys
import pickle
import parse_sentence

################################################################################

def parse_input_file(file_name):
    input_file = open(sys.argv[1],'r')
    trees = input_file.read().split("\n\n")
    parsed_trees = []
    for tree in trees:
        parsed_trees.append([line.split('\t') for line in tree.split('\n') if len(line) > 0])
    return parsed_trees

################################################################################

def parse_input_tree(tree):
    tree = tree.split('\n')
    tree_parsed = []
    for line in tree:
        tree_parsed.append(line.split('\t'))
    return tree_parsed

#############################################################################

def add_tokens_to_sentence(dependency_tree):
    tree = parsed_dep_tree[:]
    j=0
    for i in range(len(parsed_dep_tree)):
        line = parsed_dep_tree[i]
        if int(line[0]) == (i + j + 1):
            continue
        # Join token must have been present in the original sentence here
        else:
            if (i + j) < len(tree):
                # It is not the last token of sentence -> insert
                tree.insert(i+j, [str(i+j+1),tokens[i+j],'_','PUNCT','PUNCT','_','-10000','_','_','_'])
            else:
                tree.append([str(i+j+1),tokens[i+j],'_','PUNCT','PUNCT','_','-10000','_','_','_'])
            j = j + 1

    return tree

##################################################################################

def create_dict(tree):
	dict_list = dict()
	dep_tree = dict()
	dict_list[0] = {'index':0,'word':'///root','root':None}
	for line in tree:
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

###################################################################################

def return_root(tree):
	for line in tree:
		if tree[line]['root'] == 0:
			return line
	return False

##################################################################################

def add_multi_clause_to_file(multi_clause_list):
    with open('clause-treebank.conllu','a') as conllu_file:
        for tree in multi_clause_list:
            for line in tree:
                conllu_file.write("\t".join(line) + "\n")
            conllu_file.write("\n")

##############################################################################

def return_children(dep_tree, parent):
    children = [key  for (key, value) in dep_tree.items() if value == parent]
    return children

##########################################################################################

def create_clause_sentence(clause_dict, dict_of_tree, newclause, output_file):
    xi = 1
    for index, newclause in sorted(clause_dict.items(), key=lambda hoc: hoc[1][-1]):
        if newclause == []:
            continue
        wordclause = dict_of_tree[newclause.pop(0)]['word']
        for ind in newclause:
            if ind not in dict_of_tree:
                continue
            if dict_of_tree[ind]['cpos'] == 'PUNCT':
                wordclause += dict_of_tree[ind]['word']
            else:
                wordclause += ' ' + dict_of_tree[ind]['word']
        output_file.write("Clause"+str(xi)+ ": "+ wordclause + "\n")
        xi += 1
    output_file.write("\n\n")
    output_file.close()

#################################################################################################

trees = parse_input_file(sys.argv[1])
location_of_jar = sys.argv[2]
# print("===================== TREE =====================")
# print(trees)

multi_clause_list = []
verb_list = ['V']
ignCount = 0
for tree in trees:
    verb_count = 0
    for line in tree:
        # Sentence description and text is ignored
        if line[0][0] == '#':
            continue

        # reached end of sentence -> fullstop 
        if '.' in line[0]:
            ignCount += 1
            verb_count = 0
            break

        # finding verbs in the sentence
        if line[3] == 'VERB':
            verb_count += 1

    # adding trees with more than one clause to a list
    if verb_count > 2:
        # print(tree)
        multi_clause_list.append(tree)

print("Number of sentences with more than two clauses: ",len(multi_clause_list))

# Sample Sentence
input_sentence = input("Enter a Sentence to test--> ")

# Get the dependency parse tree and tokens for the input
dependency_tree, tokens = parse_sentence.format(input_sentence, location_of_jar)
# Converting the dependency tree to conll standard format
dependency_tree = dependency_tree.to_conll(10)

# Parse the tree
parsed_dep_tree = parse_input_tree(dependency_tree)
# print(" ============ Parsed Dependency Tree ===========")
# print(parsed_dep_tree)
if parsed_dep_tree[-1] == ['']:
	del parsed_dep_tree[-1]

# The next step is to identify joins in a sentence to detect independent clauses in a compound sentence        
parsed_dep_tree = add_tokens_to_sentence(parsed_dep_tree)
# print("========= Tree After Adding Tokens ==========")
# print(parsed_dep_tree)

# Meta data for sentences with more than one clause
meta_file = open('clause_data.pkl','wb')
pickle.dump(multi_clause_list, meta_file)

output_file = open('clause_output.txt','w')
output_file.write("Input Sentence: "+ input_sentence + '\n')

# Adding multi-clause sentences to the .conllu file
add_multi_clause_to_file(multi_clause_list)

# Considering the input sentence now
multi_clause_list = [parsed_dep_tree]

# Considering the following clause relations in sentences
clause_relations = ['parataxis','ccomp','acl','acl:relcl','advcl','conj']

for tree in multi_clause_list:
    print("----------------------------------------------------------------------------------------")
    dict_of_tree, dep_tree = create_dict(tree)
    print("====== Dictionary of Tree =====")
    print(dict_of_tree)
    print(" ======== Dependency Tree =========")
    print(dep_tree)

    # Fetch the Root of the sentence using the dictionary
    root = return_root(dict_of_tree)
    print("Root ---> ",root)

    coverage = dict()
    clause_dict = dict()
    queue = [0]
    clause = []

    # Getting the head/origin of clause
    head_of_clause = [key  for (key, value) in dep_tree.items() if value == 0][0]
    print("Head of Clause: --->", head_of_clause)
    nextclause = []
    _itr = 0

    sentence = '"'
    sentence += dict_of_tree[1]['word']
    print("Sub-sentence : ",sentence)

    for index in range(2,len(dict_of_tree)):
        if index not in dict_of_tree:
            continue
        if dict_of_tree[index]['cpos'] == 'PUNCT':
            sentence += dict_of_tree[index]['word']
        else:
            sentence += ' ' + dict_of_tree[index]['word']
    print([dict_of_tree[index]['word'] for index in range(len(dict_of_tree))])

    # Finding the dependencies by mapping clause relations
    while queue != [] or nextclause != []:
        if queue == []:
            queue = [nextclause[0]]
            newclause = []
            clause = sorted(clause)
        
            hoc = head_of_clause
            while hoc in clause:
                if hoc == 0:
                    break
                if dict_of_tree[hoc]['cpos'] == 'PUNCT':
                    break
                newclause = [hoc] + newclause
                # print("hoc and coverage[hoc]: ",hoc, len(coverage))
                coverage[hoc] = 1
                hoc -= 1

            hoc = head_of_clause + 1
            while hoc in clause:
                if dict_of_tree[hoc]['cpos'] == 'PUNCT':
                    break
                newclause.append(hoc)
                coverage[hoc] = 1
                hoc += 1

            clause_dict[_itr] = newclause
            _itr += 1
            clause = []
            head_of_clause = nextclause.pop(0)
            # print(clause, newclause, nextclause)

        parent = queue.pop(0)
        clause.append(parent)
        children = return_children(dep_tree, parent)
        newchildren = children
        # print("Parent: ",parent, "  Children---> ", children)

        for child in children:
            # Checking if the children have given relations with the root of clause
            if dict_of_tree[child]['rel'] in clause_relations and dict_of_tree[child]['pos'][0] == 'V':
                nextclause.append(child)
                newchildren.remove(child)

        # Adding new children in queue to be processed
        queue = newchildren + queue

    # Next clause under consideration
    newclause = []
    hoc = head_of_clause
    while hoc in clause:
        newclause = [hoc] + newclause
        coverage[hoc] = 1
        hoc -= 1

    hoc = head_of_clause + 1
    while hoc in clause:
        newclause.append(hoc)
        coverage[hoc] = 1
        hoc += 1
    # Sorting clause indexes
    clause = sorted(clause)
    clause_dict[_itr] = newclause
    _itr = 0
    clause = []
    xin = [hoc for hoc in range (1,len(dict_of_tree)) if hoc not in coverage.keys()]
    while xin != []:
        ind = xin.pop(0)
        for key, clause in sorted(clause_dict.items(), key=lambda hoc: hoc[1][-1]):
            if (ind+1 in clause or ind-1 in clause):
                clause.append(ind)
                clause_dict[key] = sorted(clause)
                coverage[ind] = 1
                break
        if ind not in coverage:
            xin = xin + [ind]
    # print("Clause Dictionary ----")
    # print(clause_dict)
    create_clause_sentence(clause_dict, dict_of_tree, newclause, output_file)

#################################################################################################
   










