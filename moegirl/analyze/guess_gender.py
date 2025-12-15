from utils.file import load_json, save_json, chdir_project_root

chdir_project_root()


male_attr = set(load_json('moegirl/preprocess/male_attr.json'))
female_attr = set(load_json('moegirl/preprocess/female_attr.json'))
nogender_attr = set(load_json('moegirl/preprocess/nogender_attr.json'))
char2attr = load_json('moegirl/preprocess/char2attr.json')
moegirl2bgm = load_json('bangumi/moegirl2bgm.json')
bgm_chars = load_json('bangumi/bgm_chars_full.json')

gender = {}
fcnt = 0
mcnt = 0
for k, v in char2attr.items():
    male_cnt = 0
    female_cnt = 0
    nogender_cnt = 0
    for i in v:
        if i in male_attr:
            male_cnt += 1
        elif i in female_attr:
            female_cnt += 1
        elif i in nogender_attr:
            nogender_cnt += 1

    if nogender_cnt > 0:
        # print(k, v)
        gender[k] = 'other'
        continue

    bgm_male_cnt = 0
    bgm_female_cnt = 0
    if k in moegirl2bgm:
        for bgmid in moegirl2bgm[k]:
            entry = bgm_chars[bgmid]
            bgm_gender = entry['gender']
            if bgm_gender == 'male':
                bgm_male_cnt += 1
            elif bgm_gender == 'female':
                bgm_female_cnt += 1

    if bgm_male_cnt > bgm_female_cnt:
        male_cnt += 2
    elif bgm_female_cnt > bgm_male_cnt:
        female_cnt += 2

    if male_cnt > female_cnt:
        gender[k] = 'male'
        mcnt += 1
    elif female_cnt > male_cnt:
        gender[k] = 'female'
        fcnt += 1

print('male:', mcnt)
print('female:', fcnt)
print('total:', len(gender))
print('all:', len(char2attr))
save_json(gender, 'moegirl/analyze/gender.json')
