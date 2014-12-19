import xml.etree.ElementTree as ET
import os.path as path
root_dir = path.expanduser("~/work/data/arChive/")
result_dir = root_dir + "abstract"
document_id = 1
listRecords_index = 2
metadata_index = 1
arXiv_index = 0

for data_id in range(1,8):
	tree = ET.parse("%s/data/data%d.xml"%(root_dir, data_id))
	root = tree.getroot()
	records_size = len(root[listRecords_index])
	with open("%s/data_abstract.txt"%(result_dir), 'a') as dat:
		for rI in range(records_size-1):
			for r in root[listRecords_index][rI][metadata_index][arXiv_index]:
				tag = r.tag.split('}')[1]
				if tag == "abstract":
					dat.write("%d %s\n"%(document_id, r.text.replace('\n', ' ')))
					document_id += 1
