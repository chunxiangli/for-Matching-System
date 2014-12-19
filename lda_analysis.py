import sys, os
from gensim import models
'''
The purpose of the script: sort the word in each topic according to the tf-idf weight
'''
word_num = 100
prob_thresh = 0.1

result_dir=os.path.realpath(sys.argv[1])
word_topic_pro_file="final.beta"

#word given topic proportion
word_topic_pro = []
for line in file("%s/%s"%(result_dir, word_topic_pro_file), 'r'):
		word_topic_pro.append(map(float, line.split()))

#stem list
stem_file="../stem_all_nostop.txt"
stem = []
for line in file("%s/%s"%(result_dir, stem_file), 'r'):
		stem.append(line.strip('\n'))

#print the word according to the order of word distribution probability in each topic
word_count_in_topic = []
with open("%s/sorted_beta.txt"%(result_dir), 'w') as wpfo:
	for word_pro in word_topic_pro:
		indices = range(len(word_pro))
		indices.sort(lambda x,y: -cmp(word_pro[x], word_pro[y]))
		wpfo.write('%s\n'%( ' '.join([ stem[index] for index in indices[:word_num] ])))
		word_count_in_topic.append([(index, 1) for index in indices[:word_num]])

#tf-idf on words per topic
tfidf = models.TfidfModel(word_count_in_topic)

def getKey(item):
	return item[1]

#print the remain word for each topic
result_file= open("%s/nostop_tfidf_onlytopic.txt"%(result_dir), 'w')#only conside the tf-idf within topic didstribution
for index in range(len(word_count_in_topic)):
	tfidf_top_id = tfidf[word_count_in_topic[index]]
	result_file.write(" ".join([stem[wid] for wid , tf in sorted([(wid, tf) for wid, tf in tfidf_top_id if tf > prob_thresh], key=getKey, reverse=True)])+'\n')
