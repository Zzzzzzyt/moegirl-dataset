import json

data = json.load(open('combined.json', encoding='utf-8'))


def dfs(x):
    # if type(x) == list:
    #     for i in x:
    #         dfs(i)
    # elif type(x) == dict:
    #     tmp = None
    #     for i in x.keys():
    #         if i == 'content':
    #             tmp = x[i]
    #         else:
    #             dfs(x[i])
    #     if tmp != None:
    #         x.pop('content')
    #         x.update(tmp)
    sub=x['subcategories']
    for i in sub:
        tmp=i['content']
        i.pop('content')
        i.update(tmp)
        dfs(i)


dfs(data)

json.dump(data, open('converted.json', 'w', encoding='utf-8',), ensure_ascii=False)
