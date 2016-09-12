from sys import argv
from pymongo import MongoClient
from Transformer import Transformer



if __name__ == '__main__':
    if len(argv) < 2:
        print('Must input a path')
        exit()
    path = argv[1]
    client = MongoClient('172.22.117.118')
    optimus = Transformer(client)
    print(path)
    tree = optimus.get_circle_packing_tree('//package/PackageTools/PackageInstaller/main')
    #print(tree)