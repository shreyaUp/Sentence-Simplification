# Sentence-Simplification ( Python3.x implementation)
## Course Project for Natural Language Processing (CSE 472)
### *Team Linguists*

## Problem Statement
Complex sentences create difficulties in Machine translation. It has been noticed that whenever there are more than two clauses (verbs), the translated Hindi sentence 
shows implications in fluency and faithfulness.This project deals with :
1) Identifying English sentences with more than two clauses. 
2) Additionally marking the clause boundaries. 
3) Suggest strategy for breaking sentences with more than two clauses into multiple sentences, each sentence having no more than two clauses each.

## Dataset Statistics
Dataset Used: English USD Dataset( in CoNLL-U format)
Trees: 12543
Word Count: 204607
Token Count: 204607
Dependency Relations: 378 ( 341=POS tag based, 37=(category, value) feature pairs)
Sentences with more than 2 clauses: 3604

## Code Components
1. dep_parser.py
Creates the following files:
..* A treebank for the sentences with more than two clauses, with the name clause-treebank.conllu
..* A metadata file (.pkl)

2. complete_sentence.py
Splits the sentences according to clause and attempts to form complete sentences.

## Running the code
1. Clone the github repo
2. Download the stanford dependency parserfor python from https://nlp.stanford.edu/software/lex-parser.shtml
3. First run -> python3 dep_parser.py {path to the dataset} {path to the unzipped stanford parser folder}
4. Then run this -> python3 complete_sentence.py
