#! /bin/python
import indexing
import VSM
import phrase_query
import spellcorrect_synonyms
import wildcard_conversion
import Boolean
import re
import expanded_query
import pickle


def construct_index():
    inv_dict = indexing.indexing('../Reuters')
    indexing.dumpfile(inv_dict, '../pyobjects/index.pickle')
    VSM.add_weight_to_index()
    wildcard_conversion.build_wildcard_index()


def replace(matched):
    string = matched.group('str')
    string = re.sub(' ', ' OR ', string[1:-1])
    return string


def bool_query(query, inv_dict):
    newquery = wildcard_conversion.wildcard_filter(query)
    newquery = re.sub(r'(?P<str>\*[^*]+\*)', replace, newquery)
    doc_list = Boolean.handle_boolean(newquery, inv_dict)
    newquery = re.sub(r'AND|OR|NOT', "", newquery)
    query_termlist = indexing.get_term_list(newquery)
    VSM.print_articles(query_termlist, doc_list)
    print(doc_list)


def free_query(query, k, inv_dict):
    newquery = wildcard_conversion.wildcard_filter(query).replace('*', ' ')
    doc_list, updated_query = expanded_query.get_query_expanded(
        newquery, k, inv_dict)
    query_termlist = indexing.get_term_list(updated_query)
    VSM.print_articles(query_termlist, doc_list)
    print(doc_list)


def main():
    while True:
        choice = input(
            "Please choose the choices below:\n1.Constructing index 2.Search\n")
        if(choice == "1"):
            construct_index()
        elif(choice == "2"):
            query = input("Please input query\n")
            bool_pattern = re.compile(r'AND|OR|NOT')
            with open('../pyobjects/weighted_index.pickle', 'rb') as pickfile:
                inv_dict = pickle.load(pickfile)
            if bool_pattern.search(query):
                bool_query(query, inv_dict)
            else:
                k = int(input("Please input the number of the results you want\n"))
                free_query(query, k, inv_dict)
        else:
            print("Error input!")
if __name__ == "__main__":
    main()
