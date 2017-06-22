#! /usr/bin/python
import html
import os
import pickle
import re
import chardet
import nltk.data
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer

replace_patterns = [
    (r"won\'t", r"will not"),
    (r"can\'t", r"cannot"),
    (r"i\'m", r"i am"),
    (r"ain\'t", r"is not"),
    (r"(\w+)\'ll", r"\g<1> will"),
    (r"(\w+)n\'t", r"\g<1> not"),
    (r"(\w+)\'ve", r"\g<1> have"),
    (r"(\w+)\'s", r"\g<1> is"),
    (r"(\w)\'re", r"\g<1> are"),
    (r"(\w+)\'d", r"\g<1> would")]


class RegexpReplacer(object):

    def __init__(self, patterns=replace_patterns):
        self.patterns = [(re.compile(regex), repl)
                         for (regex, repl) in patterns]

    def replace(self, text):
        s = text
        for (pattern, repl) in self.patterns:
            s = re.sub(pattern, repl, s)
        return s


def get_docids(directory):
    '''
    :param directory:the directory you want to scan
    :type directory:str
    :return: docids
    :rtype: list(int)
    '''
    docids = []
    for row in os.walk(directory):
        for filename in row[2]:
            docids.append(int(filename[:-5]))
    docids.sort()
    return docids


def tokenize(text):
    '''
    :param text:full text to be tokenized
    :type text:str
    :return tokens:tokenized words
    :rtype: list(str)
    '''
    replacer = RegexpReplacer()
    text = replacer.replace(text)
    tokenizer = RegexpTokenizer(r"[\w,.']+[\w]+")
    tokens = tokenizer.tokenize(text)
    return tokens


def word_tag(words):
    '''
    :param words:words to be tagged
    :type words:list
    :return tagged words list using treebank tag
    :rtype list(tuple(str,str))
    '''
    return nltk.pos_tag(words)


def pos_map(treebank_tag):
    '''
    :param treebank_tag
    :type treebank_tag:str
    :return: wordnet_tag
    :rtype: str
    '''
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatize(wordtag):
    '''
    :param wordtag:word and tag in tree_bank tag form
    :type wordtag:tuple(str,str)
    :return: lemmatized_word
    :rtype: str
    '''
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(wordtag[0], pos_map(wordtag[1]))


def get_term_list(text):
    '''
    :param text:rawtext from one document
    :type text:str
    :return: lemmatized_words
    :rtype: list(str)
    '''
    lower_words = tokenize(text.lower())
    tagged_words = word_tag(lower_words)
    lemmatized_words = [lemmatize(wordtag) for wordtag in tagged_words]
    return lemmatized_words


def terms2term_pos(terms, stopwords):
    '''
    :param terms:
    :type terms:list(str)
    :param stopwords: the set of stopwords to be used
    :type stopwords:set(str)
    :return: terms_pos
    :rtype: dict(str:list(int))
    '''
    term_pos = {}
    for index, term in enumerate(terms):
        if term in stopwords:
            continue
        if term not in term_pos.keys():
            term_pos[term] = []
        term_pos[term].append(index)
    for term in term_pos.keys():
        term_pos[term].sort()
    return term_pos


def indexing_one_doc(inv_dict, title, body, docid):
    '''
    :param inv_dict: inverted_table with term as key posting_list(actually a dict) as value
    :type inv_dict:dict{str:dict{int:dict{str:object}}}
    :param title:the text of the document's title
    :type title:str
    :param body: the text of the document's body
    :type body:str
    :param docid: the docid of the document to be indexed
    :type docid:int
    '''
    # english_stops = set(stopwords.words('english'))
    english_stops = set('')
    terms_in_title = get_term_list(title)
    terms_in_body = get_term_list(body)
    term_title_pos = terms2term_pos(terms_in_title, english_stops)
    term_body_pos = terms2term_pos(terms_in_body, english_stops)
    for term in term_title_pos.keys():
        if term not in inv_dict.keys():
            inv_dict[term] = {}
        if docid not in inv_dict[term].keys():
            inv_dict[term][docid] = {}
        inv_dict[term][docid]['title_pos'] = term_title_pos[term]
    for term in term_body_pos.keys():
        if term not in inv_dict.keys():
            inv_dict[term] = {}
        if docid not in inv_dict[term].keys():
            inv_dict[term][docid] = {}
        inv_dict[term][docid]['body_pos'] = term_body_pos[term]


def indexing(directory):
    '''
    :param: directory:the directory including documents to be indexed
    :type: directory:str
    :return: inverted_table
    :rtype:dict{str:dict{int:dict{str:object}}}
    '''
    inv_dict = {}
    docids = get_docids(directory)
    for docid in docids:
        full_text = parse_html(directory, docid)
        title = full_text.split('\n', 1)[0]
        body = full_text.split('\n', 1)[1].replace('\n', ' ')
        indexing_one_doc(inv_dict, title, body, docid)
    return inv_dict


def parse_html(directory, docid):
    '''
    :param directory: directory including htmlfiles
    :type directory:str
    :param docid:the docid of the html file to be parsed
    :type docid:int
    :return: full_text
    :rtype: str
    '''
    with open(directory + '/' + str(docid) + '.html', 'rb') as htmlfile:
        rawdata = htmlfile.read()
        encoding = chardet.detect(
            rawdata)['encoding']
        full_text = rawdata.decode(encoding)
        full_text = html.unescape(full_text)
    return full_text


def dumpfile(pyobject, filename):
    '''
    :param pyobject:python object to be dump
    :type pyobject:object
    :param filename:where to store
    :type filename:str
    '''
    with open(filename, 'wb') as file:
        pickle.dump(pyobject, file)


def main():
    inv_dict = indexing('../Reuters')
    dumpfile(inv_dict, '../pyobjects/index.pickle')
    # with open('../pyobjects/index_no_stopwords.pickle', 'rb') as pickfile:
    #     inv_dict = pickle.load(pickfile)
    # print(inv_dict)
    # for key, value in inv_dict.items():
    # if len(key) == 2:
    # print(key)
if __name__ == "__main__":
    main()
