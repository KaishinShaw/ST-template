# process_integers.py

import argparse

def process_arguments():
    """ Parse command line arguments and process them. """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('id', type=str, help='Identifier of the dataset.')
    parser.add_argument('n_clusters', type=int, help='Number of clusters.')

    args = parser.parse_args()

    section_id = args.id
    n_clusters = args.n_clusters

    # 这里可以添加处理这些变量的逻辑
    print(f"Dataset ID: {section_id}")
    print(f"Number of clusters: {n_clusters}")

if __name__ == "__main__":
    process_arguments()