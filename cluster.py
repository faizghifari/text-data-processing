import json
import requests

if __name__ == "__main__":
    with open('kemendikbud/kemendikbud_all.json', 'r', encoding='utf8') as f:
        base = json.load(f)
    
    word_freqs = {}
    results = base['results']
    for r in results:
        for c in r['list of concept']:
            tokens = c['sentiment marker'].split(' ')
            for t in tokens:
                if t not in word_freqs.keys():
                    word_freqs[t] = 1
                else:
                    word_freqs[t] += 1
    word_freqs = {k: v for k, v in sorted(word_freqs.items(), key=lambda item: item[1], reverse=True)}
    with open('word_freqs.json', 'w', encoding='utf8') as f:
        json.dump(word_freqs, f)

    # concepts = {}
    # results = base['results']
    # for r in results:
    #     for c in r['list of concept']:
    #         concept = c['concept'].strip()
    #         if concept not in concepts:
    #             concepts[concept] = {
    #                 'negative': [],
    #                 'positive': []
    #             }
    #         mark = c['sentiment marker']
    #         if mark.strip():
    #             if c['sentiment'] == 'negative':
    #                 concepts[concept]['negative'].append(mark)
    #             else:
    #                 concepts[concept]['positive'].append(mark)

    # response = requests.post('http://10.181.131.244:4110/clustering_dev', json={
    #     'project_id': 12,
    #     'concepts': concepts
    # }, headers={
    #     'x-api-key': '3b765f13e88d7072e3b51f29b5e30faff9020720953ddb7ea1507b973a0316fb'
    # })
    # with open('clusters.json', 'w', encoding='utf8') as f:
    #     json.dump(response.json(), f)

    # negatives = []
    # positives = []

    # results = base['results']
    # for r in results:
    #     for c in r['list of concept']:
    #         if c['sentiment'] == 'negative':
    #             if c['sentiment marker'] not in negatives:
    #                 negatives.append(c['sentiment marker'])
    #         else:
    #             if c['sentiment marker'] not in positives:
    #                 positives.append(c['sentiment marker'])
    
    # print('Cluster Negatives . . .')
    # response = requests.post('http://10.181.131.251:4661/hdbscan', json={
    #     'project_id': 'test project',
    #     'texts': negatives,
    #     'load': True,
    #     'sentiment': 'negative'
    # })
    # with open('negative.json', 'w', encoding='utf8') as f:
    #     json.dump(response.json(), f)

    # positives.append('haznitrama')
    # print('Cluster Positives . . .')
    # response = requests.post('http://10.181.131.251:4660/dbscan', json={
    #     'project_id': 'test project',
    #     'texts': positives,
    #     'load': True,
    #     'sentiment': 'positive'
    # })
    # with open('positive.json', 'w', encoding='utf8') as f:
    #     json.dump(response.json(), f)
