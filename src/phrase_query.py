import copy
import pickle
import VSM
import indexing


def pos_list_merge(list1, list2):
    '''
:param list1: positions of the former words
:type list1: list[int]
:param list2: positions of the next word
:type list2: list[int]
:return: list
:rtype: list[int]
    '''
    p1 = 0
    p2 = 0
    list = []
    while p1 < len(list1) and p2 < len(list2):
        diff = list2[p2] - list1[p1]
        if diff == 1:
            list.append(list2[p2])
            p1 += 1
            p2 += 1
        elif diff > 1:
            p1 += 1
        elif diff < 1:
            p2 += 1
    return list


def compute_doc_score_phrase_version(term_list, inv_dict):
    '''
    :param term_list: the list of the query terms
    :type term_list: list(str)
    :param inv_dict: the weighted inverted index
:type inv_dict: dict
    '''
    flag = 1
    for item in term_list:
        term_dict = copy.deepcopy(inv_dict[item])
        if flag:
            doc_score = copy.deepcopy(term_dict)
            flag = 0
        else:
            for doc_id in list(doc_score.keys()):
                if doc_id in term_dict:
                    if 'title_pos' in doc_score[doc_id]:
                        list1_title = doc_score[doc_id]['title_pos']
                    else:
                        list1_title = []
                    if 'title_pos' in term_dict[doc_id]:
                        list2_title = term_dict[doc_id]['title_pos']
                    else:
                        list2_title = []
                    list_title = pos_list_merge(list1_title, list2_title)
                    if 'body_pos' in doc_score[doc_id]:
                        list1_body = doc_score[doc_id]['body_pos']
                    else:
                        list1_body = []
                    if 'body_pos' in term_dict[doc_id]:
                        list2_body = term_dict[doc_id]['body_pos']
                    else:
                        list2_body = []
                    list_body = pos_list_merge(list1_body, list2_body)
                    if len(list_title) or len(list_body):
                        doc_score[doc_id][
                            'weight'] += term_dict[doc_id]['weight']
                        doc_score[doc_id]['title_pos'] = list_title
                        doc_score[doc_id]['body_pos'] = list_body
                    else:
                        del doc_score[doc_id]
                else:
                    del doc_score[doc_id]

    new_doc_score = {}
    for doc_id in doc_score:
        new_doc_score[doc_id] = doc_score[doc_id]['weight']
    doc_score = new_doc_score
    return doc_score


def phrase_query(term_list, K, inv_dict):
    '''
    :param term_list: the list of the query terms
    :type term_list: list(str)
:param K: the number of the returning docs
:type K: int
:param inv_dict: the weighted inverted index
:type inv_dict: dict
:return: doc_list
:rtype: list[int]
    '''
    # for i in range(len(term_list)):
    #     if term_list[i] not in inv_dict.keys():
    #         # call the spelling correction function
    #         term[i] = spelling_correction(term[i])

    doc_score = compute_doc_score_phrase_version(term_list, inv_dict)

    # while len(doc_score) < K:
    #     # find the term of the least frequency in the query list
    #     i = VSM.find_least_term(term_list, inv_dict)
    #     term[i] = spelling_correction(term[i])
    #     doc_score = compute_doc_score_phrase_version(term_list, inv_dict)
    doc_list = VSM.topK(doc_score, K)
    return doc_list


def main():
    with open('../pyobjects/weighted_index.pickle', 'rb') as pickfile:
        inv_dict = pickle.load(pickfile)
    while(1):
        query = input("Please put in the query:\n")
        K = input(
            "Please put in the the number of how many articles you want to find:\n")
        print("The result is:")
        query_termlist = indexing.get_term_list(query)
        doc_list = phrase_query(query_termlist, int(K), inv_dict)
        VSM.print_articles(query_termlist, doc_list)

if __name__ == "__main__":
    main()
