import numpy as np
from utils.file import load_json, chdir_project_root
from sklearn.cluster import KMeans
import sklearn.decomposition
import matplotlib.pyplot as plt
import random

chdir_project_root()

random.seed(42)
np.random.seed(42)

chars = load_json('bangumi/subset/bgm20000_subset.json')[:3000]
charmap = dict(map(lambda x: (x[1], x[0]), enumerate(chars)))


hair_color_attr = load_json('moegirl/preprocess/hair_color_attr.json')
eye_color_attr = load_json('moegirl/preprocess/eye_color_attr.json')

attrs = load_json('moegirl/preprocess/attr_index.json')
for i in hair_color_attr:
    attrs.remove(i)
for i in eye_color_attr:
    attrs.remove(i)

attrmap = dict(map(lambda x: (x[1], x[0]), enumerate(attrs)))
char2attr = load_json('moegirl/preprocess/char2attr.json')

char_count = len(chars)
attr_count = len(attrs)

data = np.zeros(shape=[char_count, attr_count], dtype=np.bool_)
for i in range(char_count):
    moeid = chars[i]
    for j in char2attr[moeid]:
        if j in attrmap:
            attrid = attrmap[j]
            data[i][attrid] = True

print(data.shape)
# print(np.sum(data))

n_clusters = 16

# pca = sklearn.decomposition.PCA(n_components=n_clusters)
pca = sklearn.decomposition.MiniBatchSparsePCA(n_components=n_clusters, batch_size=30)
# pca = sklearn.decomposition.SparsePCA(n_components=n_clusters, max_iter=100)
pca.fit(data)
reduced_data = pca.transform(data)
print(reduced_data.shape)

for i, component in enumerate(pca.components_):
    largest_indices = np.argsort(np.abs(component))[-5:][::-1]
    largest_attrs = [(attrs[idx], round(component[idx], 3)) for idx in largest_indices]
    print(f"component {i}: {largest_attrs}")

bins = [[] for i in range(n_clusters)]
for i in range(char_count)[:2000]:
    for j in range(n_clusters):
        w = reduced_data[i][j] / np.linalg.norm(reduced_data[i])
        bins[j].append((chars[i], round(w, 4)))


for j in range(n_clusters):
    bins[j].sort(
        key=lambda x: abs(x[1]),
        reverse=True,
    )

for i in range(n_clusters):
    print(f"Cluster {i}: {len(bins[i])} {bins[i][:5]}")


# pca2d = sklearn.decomposition.PCA(n_components=2)
# reduced2d = pca2d.fit_transform(reduced_data)

# # Plot the clusters
# plt.figure(figsize=(10, 7))
# centroids_2d = pca2d.transform(kmeans.cluster_centers_)
# plt.scatter(
#     centroids_2d[:, 0],
#     centroids_2d[:, 1],
#     s=300,
#     c='red',
#     marker='X',
#     label='Centroids',
# )
# for cluster in range(n_clusters):
#     cluster_data = reduced2d[clusters == cluster]
#     plt.scatter(
#         cluster_data[:, 0], cluster_data[:, 1], label=f'Cluster {cluster}', alpha=0.5
#     )

# plt.title('PCA of Character Attributes with K-means Clusters')
# plt.xlabel('Principal Component 1')
# plt.ylabel('Principal Component 2')
# plt.show()
