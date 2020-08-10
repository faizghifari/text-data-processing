import json
import glob

def read_files(file_list):
	all_lines = []
	all_text = []
	all_split_text = []
	for filename in file_list:
		print('loading', filename)
		with open(filename, encoding='latin1') as file:
			raw = file.readlines()[2:]
		raw.append('\n')
		lines = []
		text = []
		split_text = []
		for line in raw:
			if line[0]=='#':
				text.append(line[6:-1])
				lines.append([])
				split_text.append([])
			elif line[0]=='\n':
				pass
			else:
				try:
					lines[-1].append(line[:-1].split('\t'))
					split_text[-1].append(line[:-1].split('\t')[2])
				except IndexError:
					print(f'LINE: {line}')

		all_split_text += split_text
		all_lines += lines
		all_text += text

	return all_text, all_lines, all_split_text

def specific_info(data, info):
	temp = []
	prev = None
	prev_group = []
	last_none = 0

	for d in data:
		object_occured = False
		group = None

		for id in d[4].split('|'):
			if info in id:
				object_occured = True
				if len(d[4].split('[')) == 1:
					# unused
					last_none -= 1
					group = last_none
				else:
					group = int(id.split('[')[-1].split(']')[0])

				if prev != 'object' or group not in prev_group:
					temp.append({})
					prev_group.append(group)
					group_idx = prev_group.index(group)
					
					temp[group_idx]['name'] = d[2]
					temp[group_idx]['word_count'] = 1
					
					if group<0:
						temp[group_idx]['id'] = d[0]+'-0'
					else:
						temp[group_idx]['id'] = d[0]

					temp[group_idx]['aspect'] = id.split('[')[0]
					temp[group_idx]['group'] = group
					
					word_idx = int(d[0].split('-')[1])-1
					
					temp[group_idx]['word_index'] = [word_idx]

					connected_group = d[6].split('_')[0]
					if connected_group != '':
						connected_group = connected_group.split('[')[1]
						temp[group_idx]['connected_to'] = int(connected_group)
					else:
						temp[group_idx]['connected_to'] = -1

				else:
					group_idx = prev_group.index(group)
					
					temp[group_idx]['word_count'] += 1
					temp[group_idx]['name'] += (' ' + d[2])
					
					word_idx = int(d[0].split('-')[1])-1
					
					temp[group_idx]['word_index'] += [word_idx]

		if object_occured:
			prev = 'object'
		else:
			prev = None

	return temp

def get_concept(data, return_index=False, remove_deriv=False):
	temp = {}
	raw_temp = specific_info(data, 'konsep')

	if remove_deriv:
		removed = []
		for t in raw_temp:
			if t['connected_to'] != -1:
				target = t['connected_to']
				temp_target = None
				for t2 in raw_temp:
					if t2['group'] == target:
						temp_target = t2
						break
				if temp_target is None:
					removed.append(t)
					continue
				idx = t['word_index'][0]
				ref_idx = temp_target['word_index'][0]
				if ref_idx != idx+1 and ref_idx != idx-1:
					removed.append(t)
		for r in removed:
			raw_temp.remove(r)

	temp['konsep'] = raw_temp

	concepts = []
	concept_idx = []
	try:
		for info_group in temp:
			for info in temp[info_group]:
				id = info['id']
				group = info['group']
				name = info['name']
				word_idx = info['word_index']
				connect = info['connected_to']

				for i in word_idx:
					concept_idx.append(i)

				concepts.append([name, word_idx, group, id, connect])
	
	except IndexError:
		print('Data not found')
	
	if return_index:
		return concepts, concept_idx
	else:
		return concepts

def get_sentiment(data, return_index=False):
	senti = {}
	senti['positif'] = specific_info(data, 'positif')
	senti['negatif'] = specific_info(data, 'negatif')

	# join sentiment
	sentiments = []
	sentiment_idx = []
	for label in senti:
		for _senti in senti[label]:
			if len(_senti) != 0:
				group = _senti['group']
				aspect = _senti['aspect']
				target = _senti['connected_to']
				word_idx = _senti['word_index']

				for i in word_idx:
					sentiment_idx.append(i)
				
				sentiments.append([aspect, word_idx, target, group])
	
	if return_index:
		return sentiments, sentiment_idx
	else:
		return sentiments

def get_concept_sentiment(concept, concepts, sentiments):
	concept_senti = []

	try:
		for senti in sentiments:
			if senti[2] == concept[2]:
				concept_senti.append(senti[0])
		
		for c in concepts:
			if concept[2] == c[4]:
				concept_senti.extend(get_concept_sentiment(c, concepts, sentiments))
	except RecursionError:
		print(f'CONCEPT: {concept}')
		print(f'CONCEPTS: {concepts}')
		print(f'SENTIMENTS: {sentiments}')
		raise KeyboardInterrupt('ERROR')
	
	return concept_senti

def get_predecessors_c(concept, concepts):
	result = []

	try:
		for c in concepts:
			if concept[4] == c[2]:
				result.append(c)
				if c[4] != -1:
					result.extend(get_predecessors_c(c, concepts))
	except RecursionError:
		print(f'CONCEPT: {concept}')
		print(f'CONCEPTS: {concepts}')

	return result

def get_successors_s(sentiment, sentiments):
	result = []

	try:
		for s in sentiments:
			if sentiment[3] == s[2]:
				result.append(s)
	except RecursionError:
		print(f'SENTIMENT: {sentiment}')
		print(f'SENTIMENTS: {sentiments}')
	
	return result

def extract_relation_c(data, split_data):
	concepts = get_concept(data)

	result = []
	for c_ref in concepts:
		if c_ref[4] != -1:
			for c_target in concepts:
				if c_target != c_ref:
					temp_text = []
					for index, text in enumerate(split_data):
						if index in c_ref[1]:
							temp_text.append('[CONCEPT_1]')
						elif index in c_target[1]:
							temp_text.append('[CONCEPT_2]')
						else:
							temp_text.append(text)
					
					text = ' '.join(temp_text)

					if c_target[2] == c_ref[4]:
						result.append([text, 1])
					else:
						result.append([text, 0])
		
	return result

def extract_relation_s(data, split_data):
	concepts = get_concept(data)
	sentiments = get_sentiment(data)

	result = []
	for s in sentiments:
		for c in concepts:
			temp_text = []
			
			predecessors = get_predecessors_c(c, concepts)
			concept_idx = c[1]
			for p in predecessors:
				concept_idx.extend(p[1])

			for index, text in enumerate(split_data):
				if index in s[1]:
					temp_text.append('[SENTIMENT]')
				elif index in concept_idx:
					temp_text.append('[CONCEPT]')
				else:
					temp_text.append(text)
			
			text = ' '.join(temp_text)

			if s[2] == c[2]:
				result.append([text, 1])
			else:
				result.append([text, 0])

	return result

def extract_posneg(data, split_data, remove_deriv=True):
	concepts = get_concept(data)
	sentiments = get_sentiment(data)

	result = []
	if len(sentiments) > 0:
		for concept in concepts:
			if remove_deriv:
				if concept[4] != -1:
					continue

			tmp_text = []
			
			concept_senti = get_concept_sentiment(concept, concepts, sentiments)

			count_neg = concept_senti.count('negatif')
			count_pos = concept_senti.count('positif')

			for c in concepts:
				if c[4] != -1 and c[4] == concept[2]:
					if c[1][-1] == concept[1][0]-1:
						temp = c[1]
						temp.extend(concept[1])
						concept[1] = temp
					elif c[1][0] == concept[1][-1]+1:
						concept[1].extend(c[1])

			for index, text in enumerate(split_data):
				if index in concept[1]:
					tmp_text.append('[CONCEPT]')
				else:
					tmp_text.append(text)
			
			text_result = ' '.join(tmp_text)
			if count_pos == 0:
				result.append([text_result, 0])
			elif count_neg == 0:
				result.append([text_result, 1])
			else:
				result.append([text_result, 2])

	return result

def extract_posneg_v2(data, split_data):

	def add_data():
		nonlocal result
		for index, text in enumerate(split_data):
			if index in sentiment_idx:
				tmp_text.append('[SENTIMENT]')
			elif index in concept_idx:
				tmp_text.append('[CONCEPT]')
			else:
				tmp_text.append(text)
		
		text_result = ' '.join(tmp_text)
		if s[0] == 'negatif':
			result.append([text_result, 0])
		else:
			result.append([text_result, 1])

	concepts = get_concept(data)
	sentiments = get_sentiment(data)

	result = []
	if len(sentiments) > 0:
		for c in concepts:
			for s in sentiments:
				if s[2] == c[2]:
					tmp_text = []

					predecessors = get_predecessors_c(c, concepts)
					concept_idx = c[1]
					for p in predecessors:
						concept_idx.extend(p[1])

					successors = get_successors_s(s, sentiments)
					sentiment_idx = s[1]
					if len(successors) > 0:
						for suc in successors:
							sentiment_idx.extend(suc[1])
							add_data()
					else:
						add_data()
	
	result = set(tuple(r) for r in result)
	result = [list(r) for r in result]

	return result

def extract_posneg_kukt(data, split_data):

	def add_data():
		nonlocal result
		for index, text in enumerate(split_data):
			if index in concept_idx:
				tmp_text.append('[CONCEPT]')
			else:
				tmp_text.append(text)
		
		text_result = ' '.join(tmp_text)
		if s[0] == 'negatif':
			result.append([text_result, 0])
		else:
			result.append([text_result, 1])

	concepts = get_concept(data)
	sentiments = get_sentiment(data)

	result = []
	if len(sentiments) > 0:
		for c in concepts:
			for s in sentiments:
				if s[2] == c[2]:
					tmp_text = []

					predecessors = get_predecessors_c(c, concepts)
					concept_idx = c[1]
					for p in predecessors:
						concept_idx.extend(p[1])
					add_data()
	
	result = set(tuple(r) for r in result)
	result = [list(r) for r in result]

	return result

def extract_token_c_s_c(data, split_data, remove_deriv=True):
	concepts = get_concept(data, remove_deriv=remove_deriv)
	sentiments = get_sentiment(data)

	mix_idx = []
	pos_idx = []
	neg_idx = []
	if len(sentiments) > 0:
		for c in concepts:
			concept_senti = get_concept_sentiment(c, concepts, sentiments)
			count_neg = concept_senti.count('negatif')
			count_pos = concept_senti.count('positif')

			if count_pos == 0:
				neg_idx.extend(c[1])
			elif count_neg == 0:
				pos_idx.extend(c[1])
			else:
				mix_idx.extend(c[1])
	
	head_p = True
	head_n = True
	head_m = True
	token_label = []
	temp_text = []

	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in pos_idx:
			if head_p:
				token_label.append(2)
				head_p = False
			else:
				token_label.append(1)
			head_n = True
			head_m = True
		elif index in neg_idx:
			if head_n:
				token_label.append(4)
				head_n = False
			else:
				token_label.append(3)
			head_p = True
			head_m = True
		elif index in mix_idx:
			if head_m:
				token_label.append(6)
				head_m = False
			else:
				token_label.append(5)
			head_n = True
			head_p = True
		else:
			token_label.append(0)
			head_p = True
			head_n = True
			head_m = True

	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_token_c(data, split_data):
	_, concept_idx = get_concept(data, return_index=True, remove_deriv=True)
	
	head = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in concept_idx:
			if head:
				token_label.append(2)
				head = False
			else:
				token_label.append(1)
		else:
			token_label.append(0)
			head = True
	
	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_token_c_v2(data, split_data):
	concepts, concept_idx = get_concept(data, return_index=True)
	
	head_cm = True
	head_cd = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in concept_idx:
			for concept in concepts:
				if index in concept[1]:
					if concept[4] == -1:
						if head_cm:
							token_label.append(2)
							head_cm = False
						else:
							token_label.append(1)
						head_cd = True
					else:
						if head_cd:
							token_label.append(4)
							head_cd = False
						else:
							token_label.append(3)
						head_cm = True
		else:
			token_label.append(0)
			head_cm = True
			head_cd = True

	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_token_s(data, split_data):
	sentiments, sentiment_idx = get_sentiment(data, return_index=True)
	
	head_p = True
	head_n = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in sentiment_idx:
			for sentiment in sentiments:
				if index in sentiment[1]:
					if sentiment[0] == 'positif':
						if head_p:
							token_label.append(2)
							head_p = False
						else:
							token_label.append(1)
					else:
						if head_n:
							token_label.append(2)
							head_n = False
						else:
							token_label.append(1)
		else:
			token_label.append(0)
			head_p = True
			head_n = True

	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_token_c_s(data, split_data):
	_, concept_idx = get_concept(data, return_index=True, remove_deriv=True)
	sentiments, sentiment_idx = get_sentiment(data, return_index=True)
	
	head_c = True
	head_p = True
	head_n = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in concept_idx:
			if head_c:
				token_label.append(2)
				head_c = False
			else:
				token_label.append(1)
			head_p = True
			head_n = True
		elif index in sentiment_idx:
			for sentiment in sentiments:
				if index in sentiment[1]:
					if sentiment[0] == 'positif':
						if head_p:
							token_label.append(4)
							head_p = False
						else:
							token_label.append(3)
						head_n = True
					else:
						if head_n:
							token_label.append(6)
							head_n = False
						else:
							token_label.append(5)
						head_p = True
			head_c = True
			# if head_s:
			# 	token_label.append(4)
			# 	head_s = False
			# else:
			# 	token_label.append(3)
		else:
			token_label.append(0)
			head_c = True
			head_p = True
			head_n = True

	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_reason(data, split_data):
	reason = specific_info(data, 'reason')
	
	reason_idx = []
	for r in reason:
		reason_idx.extend(r['word_index'])

	head = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in reason_idx:
			if head:
				token_label.append(2)
				head = False
			else:
				token_label.append(1)
		else:
			token_label.append(0)
			head = True
	
	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_suggestion(data, split_data):
	suggestion = specific_info(data, 'suggestion')
	
	suggestion_idx = []
	for s in suggestion:
		suggestion_idx.extend(s['word_index'])

	head = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in suggestion_idx:
			if head:
				token_label.append(2)
				head = False
			else:
				token_label.append(1)
		else:
			token_label.append(0)
			head = True
	
	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_sug_reason(data, split_data):
	reason = specific_info(data, 'reason')
	suggestion = specific_info(data, 'suggestion')
	
	reason_idx = []
	for r in reason:
		reason_idx.extend(r['word_index'])

	suggestion_idx = []
	for s in suggestion:
		suggestion_idx.extend(s['word_index'])

	head_s = True
	head_r = True
	token_label = []
	temp_text = []
	for index, text in enumerate(split_data):
		temp_text.append(text)
		if index in suggestion_idx:
			if head_s:
				token_label.append(2)
				head_s = False
			else:
				token_label.append(1)
			head_r = True
		elif index in reason_idx:
			if head_r:
				token_label.append(4)
				head_r = False
			else:
				token_label.append(3)
			head_s = True
		else:
			token_label.append(0)
			head_s = True
			head_r = True
	
	result = []
	text_result = ' '.join(temp_text)
	result.append([text_result, token_label])

	return result

def extract_subjectivity(data, split_data):
	concepts = get_concept(data)
	sentiments = get_sentiment(data)

	if len(concepts) > 0 and len(sentiments) > 0:
		label = 'YES'
	else:
		label = 'NO'

	result = []
	result.append([' '.join(split_data), label])

	return result

def produce_annotation(lines, split_line, extract_type='posneg'):
	annotations = []
	i = -1
	for index, line in enumerate(lines):
		i += 1
		try:
			if extract_type == 'posneg':
				text_result = extract_posneg(line, split_line[index])
			elif extract_type == 'posneg-v2':
				text_result = extract_posneg_v2(line, split_line[index])
			elif extract_type == 'posneg-kukt':
				text_result = extract_posneg_kukt(line, split_line[index])
			elif extract_type == 'rel-c':
				text_result = extract_relation_c(line, split_line[index])
			elif extract_type == 'rel-s':
				text_result = extract_relation_s(line, split_line[index])
			elif extract_type == 'token-c':
				text_result = extract_token_c(line, split_line[index])
			elif extract_type == 'token-c-v2':
				text_result = extract_token_c_v2(line, split_line[index])
			elif extract_type == 'token-s':
				text_result = extract_token_s(line, split_line[index])
			elif extract_type == 'token-c-s':
				text_result = extract_token_c_s(line, split_line[index])
			elif extract_type == 'token-c-s-c':
				text_result = extract_token_c_s_c(line, split_line[index])
			elif extract_type == 'reason':
				text_result = extract_reason(line, split_line[index])
			elif extract_type == 'suggestion':
				text_result = extract_suggestion(line, split_line[index])
			elif extract_type == 'sug-reason':
				text_result = extract_sug_reason(line, split_line[index])
			elif extract_type == 'subjectivity':
				text_result = extract_subjectivity(line, split_line[index])

			for _text in text_result:
				annotations.append(_text)
		
		except KeyError as error:
			print(i, error)
			print()
	return annotations

# ==============================================================================================================

import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--e', type=str, required=True, help='posneg / rel-c / rel-s / token-c / token-c-v2 / token-s / token-c-s')
FLAGS, _ = parser.parse_known_args()

files_test = glob.glob('data/new/*.tsv')
# files_test = ['test.tsv']

text_test, lines_test, split_text = read_files(files_test)
annotation_test = produce_annotation(lines_test, split_text, extract_type=FLAGS.e)

file_target = 'result/cs-ku'
# file_target = 'test'
file_target += '.csv'

pos = 0
neg = 0
mix = 0

with open(file_target, 'w', newline='', encoding='utf-8') as f:
	for package in annotation_test:
		try:
			writer = csv.writer(f)
			writer.writerow([package[0], package[1]])
		except UnicodeEncodeError:
			print(package)

	f.close()
	print(f'result save to {file_target}')
	print(f'NEG: {neg}')
	print(f'POS: {pos}')
	print(f'MIX: {mix}')
