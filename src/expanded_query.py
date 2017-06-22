import sys
import pickle
import indexing
import VSM
import spellcorrect_synonyms as ss


def list2str(list):
    '''
    :param list: raw list
    :type list: str[]
    :return:string of list member with blanks
    :rtype:str
    '''
    str = ""
    for i in range(len(list)):
        str = str + list[i] + " "
    return str


def spellingcorrect_query(term_list, inv_dict):
    updated = False
    updated_term = []
    new_term_list = []
    for i in range(len(term_list)):
        if term_list[i] not in inv_dict:
            if (ss.spelling_correction(term_list[i], inv_dict) != None):
                new_term_list += ss.spelling_correction(
                    term_list[i], inv_dict)
                updated = True
    print("(Showing results for " + list2str(new_term_list) + ")")
    return new_term_list + [term for term in term_list if term in inv_dict.keys()]


def most_efficient_synonyms(raw_item, inv_dict):
    synonyms_list = ss.synonyms(raw_item)
    if (synonyms_list == None):
        return ""
    synonyms_list = [term for term in synonyms_list if term in inv_dict.keys()]
    min_length = -1
    mes = ""
    for i in range(len(synonyms_list)):
        if (len(inv_dict[synonyms_list[i]]) > min_length):
            mes = synonyms_list[i]
            min_length = len(inv_dict[synonyms_list[i]])
    return mes


def get_recommend_list(term_list, inv_dict):
    recommend_list = []
    for i in range(len(term_list)):
        mes = most_efficient_synonyms(term_list[i], inv_dict)
        if (mes != "" and mes != term_list[i]):
            temp_list = term_list[:]
            temp_list[i] = mes
            recommend_list.append(list2str(temp_list))
    recommend_list.append(list2str(term_list))
    if(len(recommend_list) > 1):
        print("there was too few results, recommended search list:")
        for i in range(len(recommend_list)):
            print(str(i) + ")" + recommend_list[i])
        select_num = input()
        return recommend_list[int(select_num)]
    else:
        return recommend_list[0]


def get_query_expanded(query, K, inv_dict):
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
    updated_term = spellingcorrect_query(term_list, inv_dict)

    doc_score = VSM.compute_doc_score(updated_term, inv_dict)

    if (len(doc_score) < K):
        updated_query = get_recommend_list(updated_term, inv_dict)
        doc_list = get_query_naive(updated_query, K, inv_dict)
    else:
        updated_query = list2str(updated_term)
        doc_list = VSM.topK(doc_score, K)
    return_tuple = (doc_list, updated_query)
    return return_tuple


def get_query_naive(query, K, inv_dict):
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
    updated_term = spellingcorrect_query(term_list, inv_dict)

    doc_score = VSM.compute_doc_score(updated_term, inv_dict)

    doc_list = VSM.topK(doc_score, K)
    return doc_list


if __name__ == "__main__":
    pass
