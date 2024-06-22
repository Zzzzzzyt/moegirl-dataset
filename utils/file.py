import json


def save_json(data, path, verbose=True):
    if verbose:
        print(f'saving to {path}')
    json.dump(
        data,
        open(path, 'w', encoding='utf-8'),
        ensure_ascii=False,
        separators=(',', ':'),
    )


def save_json_pretty(data, path, verbose=True):
    if verbose:
        print(f'saving to {path}')
    json.dump(
        data,
        open(path, 'w', encoding='utf-8'),
        ensure_ascii=False,
        separators=(',', ':'),
        indent=2,
    )


def load_json(path):
    return json.load(open(path, encoding='utf8'))
