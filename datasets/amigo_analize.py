from scipy.io import loadmat

file = 'data/AMIGOS DATASET/AMIGOS DATASET/PREPROCESSED DATA/Data_Preprocessed_P08/Data_Preprocessed_P08.mat'
data = loadmat(file)

print(data.keys())