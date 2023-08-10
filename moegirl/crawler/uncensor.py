import json
import os


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


def uncensor(name, url):
    url2 = name.replace(' ', '_')
    if url.startswith('/Category:'):
        if '/Category:'+url2 != url:
            ret = url[10:].replace('_', ' ')
            print(url, url2, ret)
            return ret, url
    else:
        if '/'+url2 != url:
            ret = url[1:].replace('_', ' ')
            print(url, url2, ret)
            return ret, url
    return name, url


def dfs(data):
    assert ('name' in data) ^ ('url' in data) == False
    if 'name' in data and 'url' in data:
        data['name'], data['url'] = uncensor(data['name'], data['url'])
    for i in data['pages']:
        i['name'], i['url'] = uncensor(i['page'], i['url'])
        del(i['page'])
    for i in data['subcategories']:
        dfs(i)


def parse(fin, fout):
    print('parse {} to {}'.format(fin, fout))
    data = json.load(open(fin, encoding='utf-8'))
    dfs(data)
    save_json(data, fout)


parse('full.json', 'uncensored.json')

for i in os.listdir('subset'):
    parse('subset/'+i, 'subset_uncensored/'+i)
