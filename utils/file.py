import json
import os


def chdir_project_root():
    root_dir = os.path.normcase(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    cur_dir = os.path.normcase(os.path.abspath(os.getcwd()))
    if cur_dir != root_dir:
        print(f'Changing working directory to project root: {root_dir}')
        os.chdir(root_dir)


def save_json(data: object, path: str, verbose: bool = True):
    if verbose:
        print(f'saving to {path}')
    json.dump(
        data,
        open(path, 'w', encoding='utf-8'),
        ensure_ascii=False,
        separators=(',', ':'),
    )


def save_json_pretty(data: object, path: str, verbose: bool = True):
    if verbose:
        print(f'saving to {path}')
    json.dump(
        data,
        open(path, 'w', encoding='utf-8'),
        ensure_ascii=False,
        separators=(',', ':'),
        indent=2,
    )


def load_json(path: str):
    return json.load(open(path, encoding='utf8'))


def load_json_or_none(path: str):
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding='utf8'))
