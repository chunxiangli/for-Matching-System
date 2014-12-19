import sys,os
from gensim import models

suffix="_nostop"
dir_root = os.path.expanduser("~/work/data/arChive/abstract")
def read_count(filename):
	count = []
	with open(filename,'r') as waf:
		for line in waf:
			word_counts = line.replace(':', ' ').split()[1:]
			count.append([ (int(word_counts[index*2]), int(word_counts[index*2+1])) for index in range(len(word_counts)/2)])
	return count[:]

corpus = read_count("%s/data_count_all%s.txt"%(dir_root, suffix))
#according to the tf-idf on the original data count, generate a reduced data count
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
doc_id = 0

#read stem
stem_all = []
with open("%s/stem_all%s.txt"%(dir_root, suffix)) as saf:
	stem_all=map(lambda x:x.strip('\n'), saf)

#threshold: 0.15
keep_stream = open("%s/tfidf_words%s.txt"%(dir_root, suffix), 'w')
reduce_stream = open("%s/reduced_words%s.txt"%(dir_root, suffix), 'w')
keep_index_list = []
keep_index_array = []
for count in corpus_tfidf:
	keep_index = []
	for index, wordprob in count:
		if wordprob > 0.15:
			keep_index.append(index)
			if index not in keep_index_list:
				keep_index_list.append(index)
	keep_stream.write(' '.join([stem_all[index] for index, wc in corpus[doc_id] if index in keep_index])+'\n')
	reduce_stream.write(' '.join([ stem_all[index] for index, wc in corpus[doc_id] if index not in keep_index])+'\n')
	keep_index_array.append(keep_index)
	doc_id += 1
reduce_stream.close()
keep_stream.close()

result_file="%s/tfidf%s_count.txt"%(dir_root, suffix)
with open(result_file, 'w') as rfw:
	keep_index_list = sorted(keep_index_list)
	for id in range(doc_id):
		reduced_count = [ '%d:%d'%(keep_index_list.index(index), wc) for index, wc in corpus[id] if index in keep_index_array[id] ]
		rfw.write("%d %s\n"%(len(reduced_count), " ".join(reduced_count)))

with open("%s/tfidf_stem%s.txt"%(dir_root, suffix), 'w') as tsw:
	tsw.write("%s"%('\n'.join([ stem_all[index] for index in keep_index_list])))


