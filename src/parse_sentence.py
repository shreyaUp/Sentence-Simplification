import subprocess
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import Tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget

def format(sentence, jar_location):
    path_to_jar = jar_location + '/stanford-parser.jar'
    path_to_models_jar = jar_location + '/stanford-parser-3.9.2-models.jar'

    dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
    tokens = word_tokenize(sentence)
    result = dependency_parser.raw_parse(sentence)

    for dep in result:
        # print(dep.tree())
        cf = CanvasFrame()
        t = dep.tree()
        tc = TreeWidget(cf.canvas(),t)
        cf.add_widget(tc,10,10)
        cf.print_to_file('tree.ps')
        cf.destroy()
        return(dep, tokens)

    
# print(format(str(input()))[0]) 
