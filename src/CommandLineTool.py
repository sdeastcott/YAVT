from sys import argv
from pymongo import MongoClient
from Transformer import Transformer


if __name__ == '__main__':
    if len(argv) < 2:
        print('Must input a path')
        exit()

    path = argv[1]
    client = MongoClient('<ip of mongo server>')
    optimus = Transformer(client)
    tree = optimus.get_circle_packing_tree('//full/perforce/path/here')
