import os
import torch
import pandas as pd
import matplotlib.pyplot as plt
import scanpy as sc
from sklearn import metrics
import multiprocessing as mp
import rpy2

from GraphST import GraphST

import argparse
# 设置 argparse 来解析命令行参数
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--datasets', type=str, required=True,
                    help='Dataset ID to process')

# 解析命令行参数
args = parser.parse_args()
# 将解析的 dataset ID 赋值给 section_id
dataset = args.datasets
section_id = dataset

# Run device, by default, the package is implemented on 'cpu'. We recommend using GPU.
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# the location of R, which is necessary for mclust algorithm. Please replace the path below with local R installation path
os.environ['R_HOME'] = '/opt/R/4.0.3/lib/R'

# the number of clusters
n_clusters = 7

result_path = f'./GraphST_results/DLPFC/{dataset}'

if not os.path.exists(result_path):
    os.makedirs(result_path)
    
# read data
file_fold = './Data/ConSpaS_DLPFC/DLPFC/' + str(dataset) #please replace 'file_fold' with the download path
adata = sc.read_visium(file_fold, count_file='filtered_feature_bc_matrix.h5', load_images=True)
adata.var_names_make_unique()

# define model
model = GraphST.GraphST(adata, device=device)

# train model
adata = model.train()

# set radius to specify the number of neighbors considered during refinement
radius = 50

tool = 'mclust' # mclust, leiden, and louvain

# clustering
from GraphST.utils import clustering

if tool == 'mclust':
   clustering(adata, n_clusters, radius=radius, method=tool, refinement=True) # For DLPFC dataset, we use optional refinement step.
elif tool in ['leiden', 'louvain']:
   clustering(adata, n_clusters, radius=radius, method=tool, start=0.1, end=2.0, increment=0.01, refinement=False)

# add ground_truth
df_meta = pd.read_csv(file_fold + '/metadata.tsv', sep='\t')
df_meta_layer = df_meta['layer_guess']
adata.obs['ground_truth'] = df_meta_layer.values

# filter out NA nodes
adata = adata[~pd.isnull(adata.obs['ground_truth'])]

# calculate metric ARI
ARI = metrics.adjusted_rand_score(adata.obs['domain'], adata.obs['ground_truth'])
adata.uns['ARI'] = ARI

print('Dataset:', dataset)
print('ARI:', ARI)

import json

json_ARI_path = f'{result_path}/{section_id}_ARI.json'

result_data = {
    'section_id': section_id,
    'Adjusted_rand_index': ARI
}

# 将结果写入JSON文件
with open(json_ARI_path, 'w') as file:
    json.dump(result_data, file)

print(f'Results saved to {json_ARI_path}')

# plotting spatial clustering result
sc.pl.spatial(adata,
              img_key="hires",
              color=["ground_truth", "domain"],
              title=["Ground truth", "ARI=%.4f"%ARI],
              show=False)
plt.savefig(f'{result_path}/ground_vs_GraphST.pdf')
plt.close()

# plotting predicted labels by UMAP
sc.pp.neighbors(adata, use_rep='emb_pca', n_neighbors=10)
sc.tl.umap(adata)
sc.pl.umap(adata, color='domain', title=['Predicted labels'], show=False)
plt.savefig(f'{result_path}/UMAP_predicted.pdf')
plt.close()