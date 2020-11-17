import os
import csv
import json
import glob
import requests

import pandas as pd

request_url_tokenize = 'http://10.181.131.244:8778/tokenizer'
headers = {'Content-Type': 'json'}

def tokenize(text):
    data = {'text': text}
    request_result = requests.post(request_url_tokenize, json=data, headers=headers).json()
    return ' '.join(request_result['tokens'])

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

					c_group = []
					connected_groups = d[6].split('|')
					for c in connected_groups:
						connected_group = c.split('_')[0]
						if connected_group != '':
							connected_group = connected_group.split('[')[1]
							c_group.append(int(connected_group))
					temp[group_idx]['connected_to'] = c_group

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

def get_concepts(line, tokens):
	concepts = []
	concepts.extend(specific_info(line, 'aspect'))
	concepts.extend(specific_info(line, 'target'))
	concepts.extend(specific_info(line, 'object'))

	sentiments = []
	sentiments.extend(specific_info(line, 'positive'))
	sentiments.extend(specific_info(line, 'negative'))

	results = []
	for s in sentiments:
		for c in concepts:
			if c['group'] in s['connected_to']:
				results.append({
					"concept": c['name'].lower(),
                    "sentiment": s['aspect'].lower(),
                    "sentiment marker": s['name'].lower()
				})

	return results

def get_subjectivity(text):
	response = requests.post('http://10.181.131.244:4445/subjectivity', json={ "texts": [text] })
	result = response.json()['results'][0]
	if result == 'YES':
		return 'subjective'
	else:
		return 'objective'

def convert(lines, texts, split_texts):
	annotations = []
	
	for index, line in enumerate(lines):
		if texts[index].strip():
			list_concepts = get_concepts(line, split_texts[index])
			annotations.append({
				"sentence": texts[index],
				"list of concept": list_concepts
			})
	
	return annotations

def write_raw_csv(tsv_files, csv_outfile):
	files = glob.glob(tsv_files)
	
	texts, lines, split_texts = read_files(files)
	raw_results = convert(lines, texts, split_texts)

	dict_list = []
	for r in raw_results:
		res_json = {}
		res_json['Sentence'] = r['sentence']
		res_json['Concept'] = []
		res_json['Sentiment'] = []
		res_json['Sentiment Marker'] = []
		for c in r['list of concept']:
			res_json['Concept'].append(c['concept'])
			res_json['Sentiment'].append(c['sentiment'])
			res_json['Sentiment Marker'].append(c['sentiment marker'])
		dict_list.append(res_json)

	if len(dict_list) > 0:
		dict_keys = list(dict_list[0].keys())
		with open(csv_outfile, 'w', encoding='utf-8', newline='') as f:
			writer = csv.DictWriter(f, fieldnames=dict_keys)
			writer.writeheader()
			for data in dict_list:
				try:
					writer.writerow(data)
				except ValueError:
					raise ValueError(f'{data}')
			f.close()
		print(f'CREATE TYPE CSV RESULTS : {csv_outfile}')

def write_raw_xls(base_output, filename):
	csv_files = glob.glob(os.path.join(base_output, '*.csv'))
	xls_writer = pd.ExcelWriter(os.path.join(base_output, filename)) # pylint: disable=abstract-class-instantiated
	for csv_file in csv_files:
		name = csv_file.split('\\')[1].split('.')[0]
		df = pd.read_csv(csv_file, encoding='utf-8')
		df.to_excel(xls_writer, sheet_name=name)
	xls_writer.save()

if __name__ == "__main__":
	tsv_paths = [
		'data/absa/Kemendikbud/priority*.tsv',
		'data/absa/Kemendikbud/kuota*.tsv',
		'data/absa/Kemendikbud/kurikulum*.tsv',
		'data/absa/Kemendikbud/kemendikbud*.tsv'
	]
	outfiles = [
		'pembelajaran jarak jauh.csv',
		'kuota bantuan.csv',
		'kurikulum darurat.csv',
		'lain-lain.csv'
	]

	base_output = 'csv'
	for i, path in enumerate(tsv_paths):
		write_raw_csv(path, os.path.join(base_output, outfiles[i]))

	# with open('kemendikbud/kemendikbud_2_kurikulum.json', 'r', encoding='utf8') as f:
	# 	base = json.load(f)
	# base = base['results']
	# base_texts = [tokenize(s['sentence']) for s in base]
	# base_subj = [s['subjectivity'] for s in base]
	# base_ids = [s['id'] for s in base]
	
	# files = glob.glob('data/absa/Kemendikbud/kurikulum*.tsv')
	
	# texts, lines, split_texts = read_files(files)
	# raw_results = convert(lines, texts, split_texts)

	# not_found = 0
	# for r in raw_results:
	# 	try:
	# 		idx = base_texts.index(tokenize(r['sentence']))
	# 		r['id'] = base_ids[idx]
	# 		r['subjectivity'] = base_subj[idx]
	# 	except ValueError:
	# 		not_found += 1
	# 		print(f"SENTENCE NOT FOUND : {r['sentence']}")
	# 		r['id'] = 0
	# 		r['subjectivity'] = get_subjectivity(r['sentence'])
	# print(f'NOT FOUND TOTAL : {not_found}')

	# chunks = [raw_results[x:x+500] for x in range(0, len(raw_results), 500)]
	# for chunk in chunks:
	# 	results = {
	# 		'results': chunk
	# 	}
	# 	print('Uploading Data . . .')
	# 	response = requests.post('http://cxa.prosa.ai/upload_data/', json=results)
	# 	print(f'Response : {response.json()}')
	
	# with open('example.json', 'w', encoding='utf8') as f:
	# 	json.dump(results, f)