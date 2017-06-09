#! /usr/bin/python
import html
import os
import pickle

import chardet
import nltk.data
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize


def tokenize(text):
    '''
    :param text:full text to be tokenized
    :type text:str
    :return tokens:tokenized words
    :rtype: list(str)
    '''
    return word_tokenize(text)


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
    return lemmatizer.lemmatize(wordtag[0], pos_map(wordtag[1])).lower()


def get_term_list(text):
    '''
    :param text:rawtext from one document
    :type text:str
    :return: lemmatized_words
    :rtype: list(str)
    '''
    raw_words = tokenize(text)
    tagged_words = word_tag(raw_words)
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
    :param inv_dict: inverted_table with term as key posting_list as value
    :type inv_dict:dict{str:list(dict)}
    :param title:the text of the document's title
    :type title:str
    :param body: the text of the document's body
    :type body:str
    :param docid: the docid of the document to be indexed
    :type docid:int
    '''
    english_stops = set(stopwords.words('english'))
    terms_in_title = get_term_list(title)
    terms_in_body = get_term_list(body)
    term_title_pos = terms2term_pos(terms_in_title, english_stops)
    term_body_pos = terms2term_pos(terms_in_body, english_stops)
    for term in term_title_pos.keys():
        if term not in inv_dict.keys():
            inv_dict[term] = []
        inv_dict[term].append(
            {'docid': docid, 'title_pos': term_title_pos[term]})
    for term in term_body_pos.keys():
        if term not in inv_dict.keys():
            inv_dict[term] = []
        if (len(inv_dict[term]) != 0) and (inv_dict[term][-1]['docid'] == docid):
            inv_dict[term][-1]['body_pos'] = term_body_pos[term]
        else:
            inv_dict[term].append(
                {'docid': docid, 'body_pos': term_body_pos[term]})


def indexing(directory):
    '''
    :param: directory:the directory including documents to be indexed
    :type: directory:str
    :return: inverted_table
    :rtype:dict{str:list(dict)}
    '''
    inv_dict = {}
    docids = []
    for row in os.walk(directory):
        for filename in row[2]:
            docids.append(int(filename[:-5]))
    docids.sort()
    for docid in docids:
        with open(directory + '/' + str(docid) + '.html', 'rb') as htmlfile:
            rawdata = htmlfile.read()
            encoding = chardet.detect(
                rawdata)['encoding']
            full_text = rawdata.decode(encoding)
            title = full_text.split('\n', 1)[0]
            body = full_text.split('\n', 1)[1].replace('\n', ' ')
            indexing_one_doc(inv_dict, title, body, docid)
    return inv_dict


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
    # inv_dict = indexing('../data/Reuters')
    # dumpfile(inv_dict, '../pyobjects/index.pickle')
    with open('../pyobjects/index.pickle', 'rb') as pickfile:
        inv_dict = pickle.load(pickfile)
    # print(inv_dict)
    # for key, value in inv_dict.items():
    #     if len(value) > 8000:
    #         print(value[:20])

if __name__ == "__main__":
    main()
