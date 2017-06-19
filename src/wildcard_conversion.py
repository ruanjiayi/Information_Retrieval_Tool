import re
import pickle
import VSM
import indexing

def build_wildcard_index():
	with open('../pyobjects/weighted_index.pickle', 'rb') as pickfile:
		inv_dict = pickle.load(pickfile)
	items=inv_dict.keys()
	#构建轮排索引
	wildcard_index={}
	for i in items:
		new_i=i+'$'
		for index in range(len(new_i)):
			wildcard_index[new_i[index:]+new_i[:index]]=i
	#写入轮排索引
	with open(r'../pyobjects/wildcard_index.pickle', 'wb') as file:
		pickle.dump(wildcard_index, file)

def wildcard_conversion(str,wildcard_index):
	'''
    :param str: string to be converted
    :type str: string
    :param wildcard_index: wildcard index
    :type wildcard_index: dictionary
	:return: list of matched string
	:rtype: list
    '''
	str=str.lower()
	new_str=str+'$'
	index=new_str.find('*')
	rindex=new_str.rfind('*')
	str_list=[]
	if index==-1:
		str_list.append(str)
		return str_list
	else:
		new_str=new_str[rindex+1:]+new_str[:index]
	#查找匹配的词
	for i in wildcard_index:
		if i.startswith(new_str):
			str_list.append(wildcard_index[i])
	#处理多个通配符的情况
	if index==rindex:
		return str_list
	else:
		new_str_list=[]
		l=re.sub('\*',r'.*',str)
		for i in str_list:
			if re.search(l,i):
				new_str_list.append(i)
		str_list=new_str_list
		return str_list

def replace(matched):
	'''
	:param matched: object matched
	:type matched: I don't know
	:return: new_str
	:rtype: string
	'''
	with open(r'../pyobjects/wildcard_index.pickle', 'rb') as pickfile:
		wildcard_index = pickle.load(pickfile)
	str=matched.group('str')
	str_list=wildcard_conversion(str,wildcard_index)
	new_str=' '.join(str_list)
	return new_str
	
	
def wildcard_filter(input):
	'''
	:param input: input needing to filt '*'
	:type input:string
	:return: new_str
	:rtype: str
	'''
	new_input=re.sub('(?P<str>[^ ]*\*[^ ]*)',replace,input)
	return new_input

if __name__ == "__main__":
	with open('../pyobjects/weighted_index.pickle', 'rb') as pickfile:
		inv_dict = pickle.load(pickfile)
	while True:
		query=input("Please put in the query:\n")
		K = input(
            "Please put in the the number of how many articles you want to find:\n")
		new_query=wildcard_filter(query)	#通配符过滤
		print("The result is:")
		query_termlist = indexing.get_term_list(new_query)
		doc_list = VSM.get_query(query_termlist, int(K), inv_dict)
		VSM.print_articles(query_termlist, doc_list)