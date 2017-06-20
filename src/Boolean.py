import pickle
import indexing
import VSM

def handle_words(tokenized_words, index, inv_dict, all_docs):
    not_flag = False
    and_flag = False
    or_flag = False
    inv_table_ans = []
    i = index
    while(i < len(tokenized_words)):
        word = tokenized_words[i]
        if word == 'NOT':
            not_flag = True
        elif word == 'AND':
            and_flag = True
        elif word == 'OR':
            or_flag = True
        else:
            lemmatized_word = indexing.get_term_list(word)
            inv_table = dict2table(inv_dict[lemmatized_word[0]])
            if or_flag == True:
                break
            else:
                if not_flag == True:
                    not_flag = False
                    inv_table = handle_not(inv_table, all_docs)
                if and_flag == True:
                    and_flag = False
                    inv_table_ans = handle_and(inv_table_ans, inv_table)
                else:
                    inv_table_ans = inv_table
        i += 1
    if or_flag == True:
        if not_flag == True:
            inv_table_ans = handle_or(inv_table_ans, handle_words(tokenized_words, i - 1, inv_dict, all_docs))
        else:
            inv_table_ans = handle_or(inv_table_ans, handle_words(tokenized_words, i, inv_dict, all_docs))
    return inv_table_ans

def dict2table(dict):
    table = []
    for term in dict.keys():
        table.append(term)
    return table

def handle_not(table, all_docs):
    ans = all_docs[:]
    for docid in table:
        try:
            ans.remove(docid)
        except ValueError:
            print('*' + str(docid))
    return ans

def handle_and(table1, table2):
    ans = []
    i1 = 0
    i2 = 0
    while(i1 < len(table1) and i2 < len(table2)):
        if table1[i1] == table2[i2]:
            ans.append(table1[i1])
            i1 += 1
            i2 += 1
        elif table1[i1] < table2[i2]:
            i1 += 1
        else:
            i2 += 1
    return ans

def handle_or(table1, table2):
    ans = []
    i1 = 0
    i2 = 0
    while (i1 < len(table1) and i2 < len(table2)):
        if table1[i1] == table2[i2]:
            ans.append(table1[i1])
            i1 += 1
            i2 += 1
        elif table1[i1] < table2[i2]:
            ans.append(table1[i1])
            i1 += 1
        else:
            ans.append(table2[i2])
            i2 += 1
    return ans

def highlight(term_list, text):
    raw_words = indexing.tokenize(text)
    lower_words = [word.lower() for word in raw_words]
    tagged_words = indexing.word_tag(lower_words)
    lemmatized_words = [indexing.lemmatize(
        wordtag) for wordtag in tagged_words]
    raw_words_tobe_highlight = [raw_words[index] for index, term in enumerate(
        lemmatized_words) if term in set(term_list)]
    highlight_set = set(raw_words_tobe_highlight)
    for word in highlight_set:
        text = text.replace(word, "\033[1;31;40m" + word + "\033[0m")
    return text

def print_articles(query_termlist, doc_list):
    '''
    :param query_termlist:
    :type query_termlist:list(str)
    :param doc_list:the id of the doc that need to be displayed
    :type doc_list:list
    '''
    directory = "../Reuters"
    for docid in doc_list:
        print(docid)
        full_text = indexing.parse_html(directory, docid)
        text = VSM.highlight(query_termlist, full_text)
        print(text)

def get_all_docs():
    ans = []
    for i in range(21576):
        if file_exists('../Reuters/' + str(i) + '.html'):
            ans.append(i)
    return ans

def file_exists(filename):
    try:
        with open(filename) as f:
            return True
    except IOError:
        return False

def main():
    with open('../pyobjects/index_no_stopwords.pickle', 'rb') as pickfile:
        inv_dict = pickle.load(pickfile)
    while (1):
        query = input("Boolean Retrieval:\n")
        print("The result is:")
        all_docs = get_all_docs()
        tokenized_words = indexing.tokenize(query)
        doc_list = handle_words(tokenized_words, 0, inv_dict, all_docs)
        query_termlist = indexing.get_term_list(query)
        print_articles(query_termlist, doc_list)

if __name__ == "__main__":
    main()