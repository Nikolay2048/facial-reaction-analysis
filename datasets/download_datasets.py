import kagglehub

# fer
# Download latest version
path = kagglehub.dataset_download("msambare/fer2013")
wiki = "https://www.wikiart.org/"
print("Path to dataset files:", path)


# pip install kagglehub
import kagglehub
import shutil
import os



# CK+
target_dir = "./data"

path = kagglehub.dataset_download("davilsena/ckdataset")

os.makedirs(target_dir, exist_ok=True)

shutil.copytree(path, target_dir, dirs_exist_ok=True)

print("Dataset copied to:", target_dir)


# Amigos
import kagglehub

# Download latest version
path = kagglehub.dataset_download("nsut123/amigos-dataset")

print("Path to dataset files:", path)

shutil.copytree(path, target_dir, dirs_exist_ok=True)

print("Dataset copied to:", target_dir)


path = kagglehub.dataset_download("steubk/wikiart")

print("Path to dataset files:", path)

shutil.copytree(path, target_dir+'/wiki_art/', dirs_exist_ok=True)

print("Dataset copied to:", target_dir)



# Download latest version
path = kagglehub.dataset_download("ngothienphu/affectnet")

print("Path to dataset files:", path)

shutil.copytree(path, target_dir+'/affectnet/', dirs_exist_ok=True)

print("Dataset copied to:", target_dir)