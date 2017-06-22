import os
import pickle
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import enchant
import indexing
import VSM


def spelling_correction(raw_term, inv_dict):
    '''
    :param raw_term:the term needing spelling correction
    :type raw_term: str
    :return: corrected term
    :rtype: str
    '''
    corrector = enchant.Dict("en_US")
    if (raw_term.strip() == ""):
        return
    if (corrector.check(raw_term) == True):
        return
    else:
        return [term for term in corrector.suggest(raw_term) if term in inv_dict.keys()]


def synonyms(raw_term):
    '''
    :param raw_term: single term to find synonyms
    :type raw_term: str
    :return: synonyms_list
    :rtype: list[str]
    '''
    if (raw_term.strip() == ""):
        return
    synonyms_list = [x.name().split(".")[0] for x in wn.synsets(raw_term)]
    synonyms_list = sorted(set(synonyms_list), key=synonyms_list.index)
    return synonyms_list


# if __name__ == "__main__":
#     with open('../pyobjects/weighted_index.pickle', 'rb') as pickfile:
#         inv_dict = pickle.load(pickfile)
#     while(1):
#         term=input()
#         print(spelling_correction(term))
#         print(synonyms(term))
