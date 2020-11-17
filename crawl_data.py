import os
import re
import json
import requests

pjj_concepts = [
        "kuliah online",
        "sekolah online",
        "pembelajaran jarak jauh",
        "kelas online",
        "ujian online",
        "belajar online",
        "pendidikan online",
        "video ospek online",
        "belajar dari rumah",
        "sekolah dari rumah",
        "kuliah dari rumah"
    ]

kemendikbud_synonyms = {
    "pjj": "pembelajaran jarak jauh",
    "pembelajaran tatap muka": "pembelajaran offline",
    "kuliah tatap muka": "kuliah offline",
    "kuliah daring": "kuliah online",
    "sekolah tatap muka": "sekolah offline",
    "sekolah daring": "sekolah online",
    "subsidi kuota": "subsidi kuota internet",
    "gubernur khofifah": "gubernur jatim",
    "khofifah indar parawansa": "gubernur jatim",
    "ganjar pranowo": "gubernur jateng",
    "ganjarpranowo": "gubernur jateng",
    "menteri nadiem": "mendikbud",
    "nadiem makarim": "mendikbud",
    "makarim": "mendikbud",
    "nadiem": "mendikbud",
    "ganjar": "gubernur jateng",
    "menteri pendidikan": "mendikbud",
    "gubernur khofifah indar": "gubernur jatim",
    "pembelajaran online": "pembelajaran jarak jauh",
    "khofifah gubernur": "gubernur jatim",
    "khofifah": "gubernur jatim",
    "khofifah gubernur jawa": "gubernur jatim",
    "parawansa": "gubernur jatim",
    "online class": "kelas online",
    "ridwan": "gubernur jabar",
    "kamil": "gubernur jabar",
    "ridwan kamil": "gubernur jabar",
    "rk": "gubernur jabar",
    "mendikbud nadiem makarim": "mendikbud",
    "mendikbud nadiem": "mendikbud",
    "gubernur jawa timur": "gubernur jatim",
    "gmeet": "google meet",
    "g meet": "google meet",
    "Kemdikbud_RI": "kemendikbud",
    "kemdikbud": "kemendikbud",
    "belajar di rumah": "belajar dari rumah",
    "ujian daring": "ujian online",
    "kuliah di rumah": "kuliah dari rumah",
    "sekolah di rumah": "sekolah dari rumah",
    "ospek daring": "ospek online",
    "pendidikan daring": "pendidikan online",
    "materi daring": "materi online",
    "sistem pembelajaran jarak jauh": "pembelajaran jarak jauh",
    "sistem pembelajaran daring": "pembelajaran jarak jauh",
    "sistem kuliah online": "kuliah online",
    "online classes": "kelas online",
    "perkuliahan online": "kuliah online",
    "online school": "sekolah online",
    "kelas daring": "kelas online",
    "tugas daring": "tugas online",
    "metode pembelajaran jarak jauh": "pembelajaran jarak jauh",
    "belajar daring": "belajar online",
    "pembelajaran secara daring": "pembelajaran jarak jauh",
    "pembelajaran secara online": "pembelajaran jarak jauh",
    "bantuan kuota internet": "bantuan kuota",
    "bantuan kuota belajar": "bantuan kuota",
    "subsidi kuota internet gratis": "subsidi kuota",
    "kuota bantuan belajar": "kuota bantuan",
    "bantuan kuota kemendikbud": "bantuan kuota",
    "subsidi kuota kemendikbud": "subsidi kuota",
    "kuota bantuan kemendikbud": "kuota bantuan",
    "bantuan kuota data": "bantuan kuota",
    "kuota bantuan pemerintah": "kuota bantuan",
    "pembelajaran daring": "pembelajaran jarak jauh"
}

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

def split(text):
    response = requests.post('http://10.181.131.244:8778/tokenizer',
                             json={ 'text': text })
    tokens = response.json()['tokens']

    return tokens

def split_and_rebuild(text):
    response = requests.post('http://10.181.131.244:8778/tokenizer',
                             json={ 'text': text })
    tokens = response.json()['tokens']
    
    if tokens is not None:
        sentence = ' '.join(tokens)
    else:
        sentence = ''

    return sentence

def preprocessing_text(text):
    regex = re.split('\n|\r', text)
    
    term = ' '.join(regex)
    term = re.sub(' +', ' ', term)
    term = re.sub(r'>?[\:\;X]+[\-=]*[3\)D\(>sp}]+', '', term)
    term = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', '', term)
    term = re.sub(r'\#\S*', '', term)
    term = re.sub(r'\&amp\;', '', term)
    term = re.sub(r'\& amp \;', '', term)
    term = deEmojify(term)
    term = split_and_rebuild(term)
    
    return term

def get_index(tokens, obj):
    results = []
    obj = obj.split()
    cekidx = None
    tokens = [re.sub(r'@', '', tok) for tok in tokens]
    tokens = [tok.lower() for tok in tokens]
    for index, _ in enumerate(tokens):
        if (len(obj) > 1):
            if index+1 < len(tokens):
                if (obj[0] == tokens[index] and 
                    obj[1] == tokens[index+1] and 
                    obj[-1] == tokens[index+len(obj)-1]):
                    cekidx = index
                    break
        else:
            if obj[0] == tokens[index]:
                cekidx = index
                break

    if cekidx is not None:
        results = list(range(cekidx, cekidx + len(obj)))
    
    return results

def crawl_data(url,
               interval=100,
               counter=0,
               counter_limit=437,
               sentence_limit=99999, 
               separated_concepts=[]):

    sentences = []
    sep_sentences = []

    while (len(sentences) < sentence_limit and
           counter < counter_limit and 
           (len(sep_sentences) < sentence_limit or separated_concepts == [])):
        print(f'Iteration Number - {counter}')

        response = requests.get(f'{url}&start={(interval * counter) + 1}&end={interval * (counter + 1)}')
        results = response.json()

        for s in results['sentences']:
            is_sent = False
            is_separate = False
            for c in s['list of concept']:
                if c['sentiment marker'] != "":
                    is_sent = True

                if c['concept'] in separated_concepts:
                    is_separate = True

                if is_sent and is_separate:
                    break

            if len(s['list of concept']) > 0 and is_sent:
                if is_separate and s not in sep_sentences:
                    s['sentence'] = preprocessing_text(s['sentence'])
                    if s['sentence']:
                        sep_sentences.append(s)
                elif s not in sentences:
                    s['sentence'] = preprocessing_text(s['sentence'])
                    if s['sentence']:
                        sentences.append(s)
            # elif len(s['list of concept']) == 0:
            #     s['sentence'] = preprocessing_text(s['sentence'])
            #     if s['sentence']:
            #         sentences.append(s)

        counter += 1

        print(f'Current sentences : {len(sentences)}')
        print(f'Current sep_sentences : {len(sep_sentences)}')

    return sentences, sep_sentences

def write_to_datasaur(sentences, 
                      folder_path, 
                      filename,
                      sep_chunk=500,
                      ext='.tsv', 
                      start_num=1, 
                      synonyms=None):

    chunks = [sentences[x:x+sep_chunk] for x in range(0, len(sentences), sep_chunk)]
    file_num = start_num

    for chunk in chunks:
        char_idx = 0
        object_id = 1

        file_name = os.path.join(folder_path, filename + str(file_num) + ext)

        if os.path.isfile(file_name):
            file_num += 1
            continue

        with open(file_name, 'w', encoding='utf-8') as f:
            print(f'Writing to file {file_name}')

            f.write('#FORMAT=Datasaur TSV 3\n\n')
            
            for idx, s in enumerate(chunk):
                # print(f'Write data number - {idx}')

                f.write(f"#Text={s['sentence']}\n")

                tokens = split(s['sentence'])
                concepts = []
                sentiments = []
                for c in s['list of concept']:
                    existing_c = None
                    for cx in concepts:
                        if c['concept'] in cx:
                            existing_c = cx
                            break
                    if existing_c is None:
                        try:
                            c_index = get_index(tokens, c['concept'])
                        except IndexError:
                            if synonyms is not None:
                                keys = [key for key,value in synonyms.items() if value == c['concept']]
                                c_index = None
                                for k in keys:
                                    try:
                                        c_index = get_index(tokens, k)
                                    except IndexError:
                                        pass
                                if c_index is None:
                                    raise IndexError(f"Error at : {s}")
                            else:
                                raise IndexError(f"Error at : {s}")
                        existing_c = (c['concept'], object_id, c_index)
                        concepts.append(existing_c)
                        object_id += 1
                    
                    if c['sentiment marker'] != "":
                        existing_s = None
                        for sx in sentiments:
                            if c['sentiment marker'] in sx:
                                existing_s = sx
                                break
                        if existing_s is None:
                            c['sentiment marker'] = preprocessing_text(c['sentiment marker'])
                            try:
                                s_index = get_index(tokens, c['sentiment marker'])
                            except IndexError:
                                if c['sentiment marker'] == '':
                                    break
                                raise IndexError(f'Error at : {c}')
                            c_target = [existing_c[1]]
                            c_sents = c['sentiment']
                            existing_s = (c['sentiment marker'], object_id, s_index, c_target, c_sents)
                            sentiments.append(existing_s)
                            object_id += 1
                        else:
                            existing_s[3].append(existing_c[1])

                for i, t in enumerate(tokens):
                    label_print = []
                    star_print = '_'
                    target_print = '_'
                    for c in concepts:
                        if i in c[2]:
                            label_print.append(f'concept[{c[1]}]')
                            break
                    
                    for s in sentiments:
                        if i in s[2]:
                            head = s[2].index(i) == 0
                            label_print.append(f'{s[4]}[{s[1]}]')
                            if head:
                                target_print = '|'.join([f'[{target}_{s[1]}]' for target in s[3]])
                                star_print = '|'.join(['*'] * len(s[3]))
                            break

                    if len(label_print) == 0:
                        label_print = '_'
                    else:
                        label_print = '|'.join(label_print)

                    f.write(f'{idx+1}-{i+1}\t{char_idx}-{char_idx+len(t)}\t{t}\t_\t{label_print}\t{star_print}\t{target_print}\t_\n')
                    char_idx += len(t) + 2
                
                f.write('\n')
            f.close()
        
        file_num += 1

def predict_cxa(sentences):
    texts = []
    for i, sent in enumerate(sentences):
        texts.append({
            "id": i,
            "text": sent['sentence']
        })
    
    synonyms = {
        "pjj": "pembelajaran jarak jauh",
        "pembelajaran tatap muka": "pembelajaran offline",
        "kuliah tatap muka": "kuliah offline",
        "kuliah daring": "kuliah online",
        "sekolah tatap muka": "sekolah offline"
    }

    defined_concepts = [
        "pembelajaran jarak jauh",
        "pembelajaran daring",
        "pembelajaran online",
        "sekolah daring",
        "sekolah online",
        "kuliah online",
        "kuliah daring",
        "pembelajaran tatap muka",
        "pembelajaran offline",
        "sekolah tatap muka",
        "sekolah offline",
        "kuliah tatap muka",
        "kuliah offline",
        "kurikulum darurat",
        "peserta didik",
        "belajar dari rumah",
        "kemendikbud",
        "guru",
        "dosen",
        "murid",
        "kelas online",
        "kuota internet",
        "paket data",
        "mendikbud",
        "rencana pelaksanaan pembelajaran",
        "kurikulum covid",
        "kurikulum kondisi khusus",
        "modul pembelajaran siswa",
        "belajar di rumah",
        "modul pembelajaran orangtua",
        "modul pembelajaran",
        "modul PJJ",
        "google classroom",
        "google meet",
        "gmeet",
        "g meet",
        "rumah belajar",
        "kunjungan guru",
        "tugas",
        "ospek online",
        "kurikulum baru",
        "pelajaran sejarah",
        "siswa"
    ]

    stopwords = [
        "gubernur",
        "gubernur jawa",
        "online",
        "offline",
        "daring"
    ]

    json_body = {
        "texts": texts,
        "defined_concepts": defined_concepts,
        "synonyms": synonyms,
        "stopwords": stopwords
    }
    headers = {
        "x-api-key": "3b765f13e88d7072e3b51f29b5e30faff9020720953ddb7ea1507b973a0316fb"
    }

    print('Predicting sentences . . .')
    response = requests.post(f'http://10.181.131.244:4111/cxp_sentiment',
                             headers=headers,
                             json=json_body)
    response = response.json()['results']
    print('Predict DONE')
    
    results = []
    if len(response) == len(sentences):
        for i, res in enumerate(response):
            results.append({
                "before": sentences[i],
                "after": res
            })
    
    results = {
        "results": results
    }
    with open('cxa_data.json', 'w', encoding='utf8') as f:
        json.dump(results, f)

if __name__ == "__main__":

    sentences, _ = crawl_data('http://cxa.prosa.ai/sentiments/?project=KPK', 
                              sentence_limit=500,
                              interval=10)

    results = {'results': sentences}
    with open('kpk/kpk.json', 'w', encoding='utf8') as f:
        json.dump(results, f)

    print('Write KPK jaga.id Data')
    write_to_datasaur(sentences, 'kpk', 'kpk_cbsa_', sep_chunk=250, start_num=1)
