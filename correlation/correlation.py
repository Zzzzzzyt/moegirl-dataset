import json
from tqdm import tqdm

char2attr = json.load(open('../preprocess/char2attr.json', encoding='utf-8'))
attr2char = json.load(open('../preprocess/attr2char.json', encoding='utf-8'))
attr_index = json.load(open('../preprocess/attr_index.json', encoding='utf-8'))


def calc_chi2(data, A, B):
    # print(A, B)
    res = [[0, 0], [0, 0]]
    for i in data:
        x = A in data[i]
        y = B in data[i]
        res[x][y] += 1
    a = res[0][0]
    b = res[0][1]
    c = res[1][0]
    d = res[1][1]
    chi2 = (a+b+c+d)*(a*d-b*c)**2/((a+b)*(c+d)*(a+c)*(b+d))
    # print('\tF\tT\t{}\nF\t{}\t{}\nT\t{}\t{}\n{}\tchi2 = {}'.format(A, a, b, c, d, B, chi2))
    return chi2, res

# print(calc_chi2('傲娇', '双马尾'))
# print(calc_chi2('傲娇', '金发'))
# print(calc_chi2('金发', '败犬'))


attrs = list(attr_index.keys())
attrs = list(filter(lambda x: len(attr2char[x]) >= 500, attrs))
print(attrs)
a = []
for i in tqdm(range(len(attrs))):
    for j in range(i+1, len(attrs)):
        A = attrs[i]
        B = attrs[j]
        chi2, res = calc_chi2(char2attr, A, B)
        if res[0][1]==0 or res[1][0]==0:
            continue
        a.append((chi2, A, B, res))
a.sort()
print(a)
json.dump(a, open('test.json', 'w', encoding='utf-8'), ensure_ascii=False)
