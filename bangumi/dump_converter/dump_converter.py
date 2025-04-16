from functools import cmp_to_key
import json
import re

from utils.file import save_json


def conv_chars():
    chars = {}
    with open("character.jsonlines", "r", encoding="utf-8") as f:
        for line in f:
            try:
                char_raw = json.loads(line)
                infobox_raw = char_raw["infobox"].replace('\r\n', '\n')[2:-2]
                infobox = []
                birthday = [None, None, None]
                blood_type = None
                gender = None
                for match in re.finditer(
                    r"\|(?P<key>.*?)=(?P<value>{.*?}|.*?)\n", infobox_raw, re.DOTALL
                ):
                    key = match.group("key").strip()
                    value = match.group("value").strip()
                    if '{' in value:
                        d = []
                        for match2 in re.finditer(
                            r"\[(?P<k>.*?)\|(?P<v>.*?)\]", value, re.DOTALL
                        ):
                            d.append(
                                {
                                    "k": match2.group("k").strip(),
                                    "v": match2.group("v").strip(),
                                }
                            )
                        infobox.append({"key": key, "value": d})
                    else:
                        infobox.append({"key": key, "value": value})
                        if key == '生日':
                            m = re.search(r"((\d*)年)?((\d*)月)?((\d*)日)?", value)
                            if m:
                                g = m.groups()
                                if g[1]:
                                    birthday[0] = int(g[1])
                                if g[3]:
                                    birthday[1] = int(g[3])
                                if g[5]:
                                    birthday[2] = int(g[5])
                        elif key == '血型':
                            value2 = value.replace('型', '').strip()
                            if value2 == 'A':
                                blood_type = 1
                            elif value2 == 'B':
                                blood_type = 2
                            elif value2 == 'AB':
                                blood_type = 3
                            elif value2 == 'O':
                                blood_type = 4
                        elif key == '性别':
                            if value != '':
                                male = False
                                female = False
                                if (
                                    '男' in value
                                    or '♂' in value
                                    or '雄' in value
                                    or '公' in value
                                ):
                                    male = True
                                if (
                                    '女' in value
                                    or '♀' in value
                                    or '雌' in value
                                    or '母' in value
                                ):
                                    female = True
                                if male and female:
                                    # print(value)
                                    pass
                                elif male:
                                    gender = "male"
                                elif female:
                                    gender = "female"
                                else:
                                    # print(value)
                                    pass
                char = {
                    'id': char_raw['id'],
                    'name': char_raw['name'],
                    'images': None,
                    'type': char_raw['role'],
                    'summary': char_raw['summary'],
                    'birth_year': birthday[0],
                    'birth_mon': birthday[1],
                    'birth_day': birthday[2],
                    'blood_type': blood_type,
                    'gender': gender,
                    'locked': False,
                    'stat': {
                        'comments': char_raw['comments'],
                        'collects': char_raw['collects'],
                    },
                    'infobox': infobox,
                }
                # print(char_raw)
                # print(char)
            except Exception as e:
                print(f"Error processing line: {e}")
                print(char_raw)
            chars[char['id']] = char
            # break

    index = []

    for k, v in chars.items():
        index.append(
            {
                'id': k,
                'name': v['name'],
                'comments': v['stat']['comments'],
                'collects': v['stat']['collects'],
            }
        )

    def cmp(a, b):
        if a['collects'] != b['collects']:
            return -a['collects'] + b['collects']
        if a['comments'] != b['comments']:
            return -a['comments'] + b['comments']
        return int(a['id']) - int(b['id'])

    index.sort(key=cmp_to_key(cmp))

    for rank, i in enumerate(index):
        i['rank'] = rank + 1

    print(index[0])
    print(index[-1])
    print('chars:', len(chars))
    save_json(index, '../bgm_index_full.json')
    save_json(chars, "../bgm_chars_full.json")


def conv_subjects():
    subjects = {}
    char2subjects = {}
    with open("subject.jsonlines", "r", encoding='utf8') as f:
        for line in f:
            subject = json.loads(line.strip())
            subjects[subject['id']] = {
                'name': subject['name'],
                'name_cn': subject['name_cn'],
            }
    with open("subject-characters.jsonlines", "r", encoding='utf8') as f:
        for line in f:
            relation = json.loads(line.strip())
            subject_id = relation['subject_id']
            if subject_id not in subjects:
                continue
            char_id = relation['character_id']
            type = relation['type']
            if type == 1:
                staff = "主角"
            elif type == 2:
                staff = "配角"
            elif type == 3:
                staff = "客串"
            else:
                staff = ""
            order = relation['order']
            if char_id not in char2subjects:
                char2subjects[char_id] = []
            char2subjects[char_id].append(
                {
                    'id': subject_id,
                    'name': subjects[subject_id]['name'],
                    'name_cn': subjects[subject_id]['name_cn'],
                    'staff': staff,
                    'order': order,
                }
            )
    for v in char2subjects.values():
        v.sort(key=lambda x: x['order'])
        for i in v:
            del i['order']
    save_json(char2subjects, "../bgm_subjects_full.json")


conv_chars()
conv_subjects()
