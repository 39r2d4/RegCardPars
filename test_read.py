import pickle

with open('data.pl', 'rb') as file:
	data_new = pickle.load(file)

for x in data_new:
	print(x)

