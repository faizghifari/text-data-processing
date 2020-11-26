import os
import json
import glob

import itertools
import argparse
import csv


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
            if line[0] == '#':
                text.append(line[6:-1])
                lines.append([])
                split_text.append([])
            elif line[0] == '\n':
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

                    if group < 0:
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


def get_relation_csug(data, split_data):
    concepts = []
    concepts.extend(specific_info(data, 'target'))
    concepts.extend(specific_info(data, 'object'))

    suggestion = specific_info(data, 'suggestion')

    results = []
    for s in suggestion:
        for c in concepts:
            temp_text = []
            for index, text in enumerate(split_data):
                if index in s['word_index']:
                    temp_text.append('[SUGGESTION]')
                elif index in c['word_index']:
                    temp_text.append('[CONCEPT]')
                else:
                    temp_text.append(text)

            text = ' '.join(temp_text)

            if s['connected_to'] == c['group']:
                results.append([text, 1])
            else:
                results.append([text, 0])

    return results


def get_relation_cs(data, split_data):
    concepts = []
    concepts.extend(specific_info(data, 'aspect'))
    concepts.extend(specific_info(data, 'target'))
    concepts.extend(specific_info(data, 'object'))

    sentiments = []
    sentiments.extend(specific_info(data, 'positif'))
    sentiments.extend(specific_info(data, 'negatif'))

    results = []
    for s in sentiments:
        for c in concepts:
            temp_text = []
            for index, text in enumerate(split_data):
                if index in s['word_index']:
                    temp_text.append('[SENTIMENT]')
                elif index in c['word_index']:
                    temp_text.append('[CONCEPT]')
                else:
                    temp_text.append(text)

            text = ' '.join(temp_text)

            if s['connected_to'] == c['group']:
                results.append([text, 1])
            else:
                results.append([text, 0])

    return results


def get_relation_at(data, split_data):
    aspects = specific_info(data, 'aspect')
    targets = specific_info(data, 'target')

    results = []
    for a in aspects:
        for t in targets:
            temp_text = []
            for index, text in enumerate(split_data):
                if index in a['word_index']:
                    temp_text.append('[ASPECT]')
                elif index in t['word_index']:
                    temp_text.append('[TARGET]')
                else:
                    temp_text.append(text)

            text = ' '.join(temp_text)

            if a['connected_to'] == t['group']:
                results.append([text, 1])
            else:
                results.append([text, 0])

    return results


def get_relation_to(data, split_data):
    targets = specific_info(data, 'target')
    objects = specific_info(data, 'object')

    results = []
    for t in targets:
        for o in objects:
            temp_text = []
            for index, text in enumerate(split_data):
                if index in t['word_index']:
                    temp_text.append('[TARGET]')
                elif index in o['word_index']:
                    temp_text.append('[OBJECT]')
                else:
                    temp_text.append(text)

            text = ' '.join(temp_text)

            if t['connected_to'] == o['group']:
                results.append([text, 1])
            else:
                results.append([text, 0])

    return results


def get_relation_sug_res(data, split_data):
    reason = specific_info(data, 'reason')
    suggestion = specific_info(data, 'suggestion')

    results = []
    for r in reason:
        for s in suggestion:
            temp_text = []

            s_idx = s['word_index']
            r_idx = r['word_index']
            for idx, text in enumerate(split_data):
                if idx in s_idx:
                    temp_text.append('[SUGGESTION]')
                elif idx in r_idx:
                    temp_text.append('[REASON]')
                else:
                    temp_text.append(text)
            text = ' '.join(temp_text)

            if r['connected_to'] == s['group']:
                results.append([text, 1])
            else:
                results.append([text, 0])

    return results


def get_relation_all(data, split_data):
    entities = []
    entities.extend(specific_info(data, 'aspect'))
    entities.extend(specific_info(data, 'target'))
    entities.extend(specific_info(data, 'object'))

    entities.extend(specific_info(data, 'positif'))
    entities.extend(specific_info(data, 'negatif'))

    entities.extend(specific_info(data, 'reason'))
    entities.extend(specific_info(data, 'suggestion'))

    combs = list(itertools.combinations(entities, 2))
    combs = [c for c in combs if c[0]['aspect'] != c[1]['aspect']]

    results = []
    for c in combs:
        if (c[0]['group'] in c[1]['connected_to'] or
                c[1]['group'] in c[0]['connected_to']):
            results.append([' '.join(split_data),
                            f"{c[0]['name']}-{c[1]['name']}",
                            1])
        else:
            results.append([' '.join(split_data),
                            f"{c[0]['name']}-{c[1]['name']}",
                            0])

    return results


def extract_token(data, split_data, label):
    labels = specific_info(data, label)

    labels_idx = []
    for l in labels:
        labels_idx.extend(l['word_index'])

    head = True
    token_label = []
    temp_text = []
    for index, text in enumerate(split_data):
        temp_text.append(text)
        if index in labels_idx:
            if head:
                token_label.append(2)
                head = False
            else:
                token_label.append(1)
        else:
            token_label.append(0)
            head = True

    results = []
    text_result = ' '.join(temp_text)
    results.append([text_result, token_label])

    return results


def extract_all_entity(data, split_data):
    aspects = specific_info(data, 'aspect')
    targets = specific_info(data, 'target')
    objects = specific_info(data, 'object')

    aspect_idx = []
    for a in aspects:
        aspect_idx.extend(a['word_index'])

    target_idx = []
    for t in targets:
        target_idx.extend(t['word_index'])

    object_idx = []
    for o in objects:
        object_idx.extend(o['word_index'])

    head_a = True
    head_t = True
    head_o = True
    token_label = []
    temp_text = []
    for index, text in enumerate(split_data):
        temp_text.append(text)
        if index in aspect_idx:
            if head_a:
                token_label.append(2)
                head_a = False
            else:
                token_label.append(1)
            head_t = True
            head_o = True
        elif index in target_idx:
            if head_t:
                token_label.append(4)
                head_t = False
            else:
                token_label.append(3)
            head_a = True
            head_o = True
        elif index in object_idx:
            if head_o:
                token_label.append(6)
                head_o = False
            else:
                token_label.append(5)
            head_a = True
            head_t = True
        else:
            token_label.append(0)
            head_a = True
            head_t = True
            head_o = True

    results = []
    text_result = ' '.join(temp_text)
    results.append([text_result, token_label])

    return results


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

    results = []
    text_result = ' '.join(temp_text)
    results.append([text_result, token_label])

    return results


def produce_annotation(lines, split_line, extract_type='posneg'):
    annotations = []
    i = -1
    for index, line in enumerate(lines):
        i += 1
        try:
            if extract_type == 'rel-csug':
                text_result = get_relation_csug(line, split_line[index])
            elif extract_type == 'rel-cs':
                text_result = get_relation_cs(line, split_line[index])
            elif extract_type == 'rel-at':
                text_result = get_relation_at(line, split_line[index])
            elif extract_type == 'rel-to':
                text_result = get_relation_to(line, split_line[index])
            elif extract_type == 'rel-sug-res':
                text_result = get_relation_sug_res(line, split_line[index])
            elif extract_type == 'rel-all':
                text_result = get_relation_all(line, split_line[index])
            elif extract_type == 'object':
                text_result = extract_token(line, split_line[index], 'object')
            elif extract_type == 'target':
                text_result = extract_token(line, split_line[index], 'target')
            elif extract_type == 'aspect':
                text_result = extract_token(line, split_line[index], 'aspect')
            elif extract_type == 'reason':
                text_result = extract_token(line, split_line[index], 'reason')
            elif extract_type == 'suggestion':
                text_result = extract_token(
                    line, split_line[index], 'suggestion')
            elif extract_type == 'sug-reason':
                text_result = extract_sug_reason(line, split_line[index])
            elif extract_type == 'all-entity':
                text_result = extract_all_entity(line, split_line[index])

            for _text in text_result:
                annotations.append(_text)

        except KeyError as error:
            print(i, error)
            print()
    return annotations


parser = argparse.ArgumentParser()
parser.add_argument('--e', type=str, required=True)
FLAGS, _ = parser.parse_known_args()

files_test = []
folders = glob.glob('data/absa/*/')
for f in folders:
    if f.split('\\')[1] == 'Kemendikbud':
        files_test.extend(glob.glob(os.path.join(f, '*.tsv')))
# files_test.extend(glob.glob('data/suggestion/aspect/*.tsv'))
# files_test = ['test.tsv']
# files_test = glob.glob('data/suggestion/aspect/*.tsv')

text_test, lines_test, split_text = read_files(files_test)
annotation_test = produce_annotation(
    lines_test, split_text, extract_type=FLAGS.e)

file_target = 'result/rel-all-kemendikbud'
# file_target = 'test'
file_target += '.csv'

with open(file_target, 'w', newline='', encoding='utf-8') as f:
    count_0 = 0
    count_1 = 0
    writer = csv.writer(f)
    if FLAGS.e == 'rel-all':
        writer.writerow(["text_a", "text_b", "label"])
    else:
        writer.writerow(["text_a", "label"])
    for package in annotation_test:
        try:
            if len(package) == 2:
                writer.writerow([package[0], package[1]])
            elif len(package) == 3:
                writer.writerow([package[0], package[1], package[2]])
                if package[2] == 0:
                    count_0 += 1
                elif package[2] == 1:
                    count_1 += 1
        except UnicodeEncodeError:
            print(package)

    f.close()
    print(f'count 0 : {count_0}')
    print(f'count 1 : {count_1}')
    print(f'results save to {file_target}')
