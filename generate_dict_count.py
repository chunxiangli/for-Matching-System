import re, sys, os
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
                                
filter_pattern = re.compile(
                             '\$.*?\$'     #filter the latex equations 
                             '|\(.*?\)'    #filter out abreviations
                             '|[^(\s|\w)]' #filter non whitespace or alphanumeric characters
                           )

def clean_word(w):
	return filter_pattern.sub('', w)

stop_words = stopwords.words('english')
abstract_dir = os.path.expanduser("~/work/data/arChive/abstract")
dictionary = {}
dic_id = 0
doc_count = {}

file_name = "%s/data_abstract.txt"%(abstract_dir)
with open(file_name) as fo:
        for line in fo:
                doc_info = clean_word(line).split()
                doc_id = int(doc_info[0])
                doc_count[doc_id] = {}
                w_id = -1
                for w in doc_info[1:]:
			w = w.lower()
			#prefilter the digits, stopwords and the word with length less than 3
                        if re.match('^[0-9]*$',w) or len(w) < 3 or  w in stop_words:
                                continue

                        if w in dictionary.keys():
                                w_id = dictionary[w]
                        else:
                                dictionary[w] = dic_id
                                w_id = dic_id
                                dic_id += 1			
                        try:
                                doc_count[doc_id][w_id] += 1
                        except:
                                doc_count[doc_id][w_id] = 1
                
from nltk.stem.porter import PorterStemmer
pstemmer = PorterStemmer()

stem_dictionary = {}
stem_keys = []
dic_id = 0
vocabulary = dictionary.keys()
new_doc_count = { d:{} for d in range(1, doc_id+1)}
for k in vocabulary:
        stem_k = pstemmer.stem(k).encode('ascii', 'ignore')
	stem_dictionary.setdefault(stem_k, []).append(k)
        if stem_k not in stem_keys:
		stem_keys.append(stem_k)

        stem_dic_id = stem_keys.index(stem_k)

        origin_k_id = dictionary[k]
        for doc_id in new_doc_count:
                if origin_k_id in doc_count[doc_id]:
                        if stem_dic_id in new_doc_count[doc_id]:
                                new_doc_count[doc_id][stem_dic_id] += doc_count[doc_id][origin_k_id]
                        else:
                                new_doc_count[doc_id][stem_dic_id] = doc_count[doc_id][origin_k_id]

with open("%s/stem_all_nostop.txt"%(abstract_dir), 'w') as dfo:	
        vocabulary = stem_keys
        for k in vocabulary:
                dfo.write("%s\n"%k)		

with open("%s/stem_dictionary_all_nostop.txt"%abstract_dir, 'w') as sdfo:
	for k in stem_dictionary:
		sdfo.write("%s:%s\n"%(k, " ".join(stem_dictionary[k])))

with open("%s/data_count_all_nostop.txt"%(abstract_dir), 'w') as dcfo:
                for doc_id in new_doc_count:
                        dcfo.write("%d %s\n"%(len(new_doc_count[doc_id]), " ".join(["%s:%d"%(word,count) for word, count in new_doc_count[doc_id].items()])))



