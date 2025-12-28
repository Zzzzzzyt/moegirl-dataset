from tqdm import tqdm
from utils.file import load_json, load_json_or_none, save_json, chdir_project_root
from utils.network import safe_get, safe_soup, safe_download

chdir_project_root()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Zzzyt/MoeRanker (https://github.com/Zzzzzzyt/MoeRanker)',
}
cooldown = 1


def get_id(id, bar):
    url = f"https://api.bgm.tv/v0/characters/{id}"
    data = safe_get(url, headers=headers, cooldown=cooldown, bar=bar).json()
    return data['id']


index = load_json('bangumi/bgm_index_full.json')
chars = load_json('bangumi/bgm_chars_full.json')
subjects = load_json('bangumi/bgm_subjects_full.json')

redirects = load_json_or_none('bangumi/bgm_redirects_full.json') or {}
# redirects = {}
# for k in redirects.keys():
#     redirects[k] = str(redirects[k])

sus = []

for k, v in subjects.items():
    if len(v) == 0:
        if int(k) < 190000:
            continue
        if k not in redirects:
            sus.append(k)

try:
    bar = tqdm(sus)
    for k in bar:
        bar.set_description(f'{k} {chars[k]["name"]}')
        realid = str(get_id(k, bar))
        if realid != k:
            redirects[k] = realid
            bar.write(f'{k} {chars[k]["name"]} -> {realid} {chars[realid]["name"]}')
except KeyboardInterrupt:
    pass


for k in redirects.keys():
    if k in chars:
        del chars[k]
    if k in subjects:
        del subjects[k]

index2 = []
for i in index:
    if i['id'] not in redirects:
        i['rank'] = len(index2) + 1
        index2.append(i)

save_json(index2, 'bangumi/bgm_index_full.json')
save_json(chars, 'bangumi/bgm_chars_full.json')
save_json(subjects, 'bangumi/bgm_subjects_full.json')
save_json(redirects, 'bangumi/bgm_redirects_full.json')
