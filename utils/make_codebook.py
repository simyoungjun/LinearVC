#%
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from tqdm import tqdm

from sklearn.cluster import MiniBatchKMeans
#%
# titles, srcs, tgts = [], [], []
wawlm_paths = []
with open('/home/yjsim/VoiceConversion/ICASSP2025/filelists/train.txt', "r") as file:
    for rawline in file.readlines()[:]:
        # title, tgt, src = rawline.strip().split("\n")

        # titles.append('src:'+src.split('/')[-1][:-4]+'&tgt:'+tgt.split('/')[-1][:-4])
        
        line = rawline[:-1]
        # srcs.append(src)
        # tgts.append(tgt)

        substring_to_replace1 = 'vctk-16k'
        
        # replacement_string1 = 'wavlm-6L' 
        replacement_string1 = 'wavlm-6L' 
        substring_to_replace2 = '.wav'
        replacement_string2 = '.pt' 
        
        wawlm_paths.append(line.replace(substring_to_replace1, replacement_string1).replace(substring_to_replace2, replacement_string2).replace('racoon_fast/sim','data/VC'))
        # src_paths_new = [src_path.replace(substring_to_replace1, replacement_string1).replace(substring_to_replace2, replacement_string2) for src_path in tgts]
  
#%

# sorted_list_1 = sorted(wawlm_paths)
# sorted_list_2 =  sorted(src_paths_new)
flag = 0
wav_num = 40000
id = 0

total = []
for path in tqdm(wawlm_paths[:wav_num]):
    tmp = np.array(torch.load(path).squeeze().transpose(0,1))

    total.append(tmp)
# total = torch.tensor(total)
concat = np.concatenate(total, axis=0)
# total = np.array(total)

# total = torch.concat((total, tmp), dim=0)
# data = total.numpy().astype(np.float32)
print(concat.shape)
save_path = '/shared/NAS_HDD/VC/codebook/'
np.save(save_path + f'VCTK_train_{wav_num}.npy', concat)
    # np.save(save_path + f'VCTK_train_{wav_num}_{i}.npy', total)
    # print(f'id : {id}, {idx_H}~{idx_T}')
    
    # idx_H += wav_num
    # idx_T += wav_num
    # id += 1
    
#%
save_path = '/shared/NAS_HDD/VC/codebook/'
np.save(save_path+f'VCTK_train_{wav_num}.npy', concat)
# # Perform t-SNE
# tsne = TSNE(n_components=3, random_state=42)
# tsne_results = tsne.fit_transform(total)

# # Plot t-SNE results in 3D
# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot(111, projection='3d')

# # Scatter plot
# sc = ax.scatter(tsne_results[:, 0], tsne_results[:, 1], tsne_results[:, 2], c='blue', alpha=0.6, s=0.1)

# # Labels and title
# ax.set_title('3D t-SNE visualization')
# ax.set_xlabel('t-SNE component 1')
# ax.set_ylabel('t-SNE component 2')
# ax.set_zlabel('t-SNE component 3')

# plt.show()
# plt.savefig('./tsne_data.png')      



#%
# from sklearn.preprocessing import StandardScaler
save_path = '/shared/NAS_HDD/VC/codebook/'

data = np.load(save_path+f'VCTK_train_40000.npy')
# data = np.load('VCTK_train_4000.npy')
print(data.shape)
print(data)

#%
n_clusters = 128
kmeans = MiniBatchKMeans(n_clusters=n_clusters,
                         random_state=42,
                         n_init="auto")


# kmeans = faiss.Kmeans(d=1024, k=256, niter=100, verbose=True)
# For GPU(s), run the following line. This will use all GPUs
# kmeans = faiss.Kmeans(d=D, k=K, niter=20, verbose=True, gpu=True)

# Run clustering
kmeans.fit(data)
kmeans.cluster_centers_
#%
print(data.shape)
wav_num=40000
torch.save(torch.from_numpy(kmeans.cluster_centers_), f'/shared/NAS_HDD/VC/codebook/VCTK_{wav_num}_{n_clusters}k_no_trim.pt')

# # Error for each iteration
# print(kmeans.obj)  # array with 20 elements

# # Centroids after clustering
# print(kmeans.centroids.shape)  # (10, 128)

# The assignment for each vector.
# dists, ids = kmeans.index.search(data, 1)  # Need to run NN search again
# print(ids.shape)  # (10000, 1)

# # Params
# print("D:", kmeans.d)
# print("K:", kmeans.k)
# print("niter:", kmeans.cp.niter)
#%
all = np.concatenate((data, kmeans.cluster_centers_))
# Perform t-SNE
tsne = TSNE(n_components=3, random_state=42)
tsne_results = tsne.fit_transform(all)


#%
# Plot t-SNE results in 3D
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot
ax.scatter(tsne_results[:data.shape[0], 0], tsne_results[:data.shape[0], 1], tsne_results[:data.shape[0], 2], c='blue', alpha=0.3, s=0.1)
# Scatter plot
ax.scatter(tsne_results[data.shape[0]:, 0], tsne_results[data.shape[0]:, 1], tsne_results[data.shape[0]:, 2], c='red', alpha=1, s=1)

# Labels and title
ax.set_title('3D t-SNE visualization')
ax.set_xlabel('t-SNE component 1')
ax.set_ylabel('t-SNE component 2')
ax.set_zlabel('t-SNE component 3')

plt.show()
plt.savefig('./tsne_codebook.png')   
#%
torch.save(torch.from_numpy(kmeans.cluster_centers_), '/shared/NAS_HDD/VC/codebook_init/VCTK_codebook_256_VCTK_train_no_trim_new.pt')
# np.save(kmeans.centroids), '/shared/racoon_fast/sim/codebook_init/codebook_2048_SrcRef.pt')
#%
kmeans.centroids.shape

#%
