from utils.file import load_json, save_json

subjects = load_json('../crawler/subjects.json')
subjects = subjects['subcategories'][3:]

ret = []
for i in subjects:
    for j in i['subcategories']:
        name, url = j['name'], j['url']
        assert '/Category:' + name.replace(' ', '_') == url
        ret.append(name)

save_json(ret, 'subject_index.json')
