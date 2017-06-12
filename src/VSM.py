# author:Jiayi Ruan
# to do list:
# 1.add spelling correction features
# 2.adjust the output form(now we only output the title of the top articles)


import pickle
import math
import indexing
# define INFINITY 100000


def compute_wf_idf(term_frequency, idf):
    '''
    :param term_frequency:the times of a term appearing in a doc
    :type document_frequency:double
    :param idf:inverse doucument frequency
    :type idf:double
    :return: weight
    :rtype: double
    '''
    if term_frequency <= 0:
        return 0.0
    wf = 1 + math.log(term_frequency)
    return wf * idf


def compute_weight(one_inv_dict, N):
    '''
    :param one_inv_dict:one inverted index record of a specific term
    :type one_inv_dict:dict(dict)
    :param N:the number of all doc
    :type N:int
    :return: weight
    :rtype: double
    '''
    # compute the total count in all doc.
    document_frequency = len(one_inv_dict)
    if document_frequency > 0:
        idf = math.log(N / document_frequency)
        for i in one_inv_dict:
            term_frequency = 0
            if 'title_pos' in one_inv_dict[i]:
                term_frequency += len(one_inv_dict[i]['title_pos'])
            if 'body_pos' in one_inv_dict[i]:
                term_frequency += len(one_inv_dict[i]['body_pos'])
            one_inv_dict[i]['weight'] = compute_wf_idf(term_frequency, idf)
    else:
        print("Error in compute_weight()")


def get_doc_count():
    return 10788


def add_weight_to_index():
    # no param no return
    # To adjust the index with add the weight to every doc record
    with open('../pyobjects/index.pickle', 'rb') as pickfile:
        inv_dict = pickle.load(pickfile)
        for term in inv_dict.keys():
            compute_weight(inv_dict[term], get_doc_count())
    with open('../pyobjects/weighted_index.pickle', 'wb') as file:
        pickle.dump(inv_dict, file)


def compute_doc_score(term_list, inv_dict):
    '''
    :param term_list:the list of input query word
    :type term_list:list[str]
    :param inv_dict:the whole inverted index
    :type inv_dict:dict{dict{dict}}
    :return: doc_score
    :rtype: dict
    '''
    doc_score = {}
    for term in term_list:
        term_dict = inv_dict[term]
        for doc_id in term_dict:
            if doc_id in doc_score:
                doc_score[doc_id] += term_dict[doc_id]['weight']
            else:
                doc_score[doc_id] = term_dict[doc_id]['weight']
    return doc_score


def topK(doc_score, K):
    '''
    :param doc_score:The score of the doc for a given term
    :type doc_score:dict
    :param K:the number of the returning docs
    :type K:int
    :return: doc_list
    :rtype: list[int]
    '''
    doc_list = sorted(doc_score, key=doc_score.get, reverse=True)
    return doc_list[:K]


def compute_term_frequency(one_inv_dict):
    '''
    :param one_inv_dict:one inverted index record of a specific term
    :type one_inv_dict:dict(dict)
    :return: term_frequency
    :rtype: double
    '''
    term_frequency = 0
    for doc_id in one_inv_dict:
        if 'title_pos' in one_inv_dict[doc_id]:
            term_frequency += len(one_inv_dict[doc_id]['title_pos'])
        if 'body_pos' in one_inv_dict[i]:
            term_frequency += len(one_inv_dict[doc_id]['body_pos'])
    return term_frequency


def find_least_term(term_list, inv_dict):
    '''
    :param erm_list:the list of the query terms
    :type erm_list:list[str]
    :param inv_dict:the weighted inverted index
    :type inv_dict:dict
    :return: index
    :rtype: int
    '''
    frequency = INFINITY
    for i in range(len(term_list)):
        term_frequency = compute_term_frequency(inv_dict[term_list[i]])
        if term_frequency < frequency:
            frequency = term_frequency
            index = i
    return index


def get_query(query, K, inv_dict):
    '''
    :param query:the query put in by users
    :type query:str
    :param K:the number of the returning docs
    :type K:int
    :param inv_dict:the weighted inverted index
    :type inv_dict:dict
    :return: doc_list
    :rtype: list[int]
    '''
    term_list = indexing.get_term_list(query)
    for i in range(len(term_list)):
        if term_list[i] not in inv_dict.keys():
            # call the spelling correction function
            term[i] = spelling_correction(term[i])
    doc_score = compute_doc_score(term_list, inv_dict)
    while len(doc_score) < K:
        # find the term of the least frequency in the query list
        i = find_least_term(term_list, inv_dict)
        term[i] = spelling_correction(term[i])
        doc_score = compute_doc_score(term_list, inv_dict)
    doc_list = topK(doc_score, K)
    return doc_list


def print_articles(doc_list):
    '''
    :param doc_list:the id of the doc that need to be displayed
    :type doc_list:list
    '''
    directory = "../Reuters"
    for doc_id in doc_list:
        print(doc_id)
        full_text = indexing.parse_html(directory, doc_id)
        print(full_text)


def main():
        # add_weight_to_index()
    with open('../pyobjects/weighted_index.pickle', 'rb') as pickfile:
        inv_dict = pickle.load(pickfile)
    while(1):
        print("Please put in the query:")
        query = input()
        print("Please put in the the number of how many articles you want to find:")
        K = input()
        print("The result is:")
        print_articles(get_query(query, int(K), inv_dict))
    #     #print(get_query(query, int(K), inv_dict))

if __name__ == "__main__":
    main()
