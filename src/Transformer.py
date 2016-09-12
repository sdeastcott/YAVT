import os
import posixpath as path
from pymongo import MongoClient
from bson.regex import Regex
from pymongo.errors import InvalidStringData
import re
from pprint import pprint


def deep_set(tree, paths, value):
    current = tree
    segment = paths.pop(0)
    current['children'].setdefault(segment, {
            'file_count': 0,
            'name': segment,
            'children': {},
    })

    if len(paths) == 0:
        current['children'][segment].update(value)
        return
    deep_set(current['children'][segment], paths, value)


def for_display(tree):
    for k, v in tree['children'].items():
        for_display(v)
    tree['children'] = [v for k, v in tree["children"].items()]
    if 'contributors' in tree:
        tree['contributors'] = sorted(tree['contributors'], cmp=lambda x, y: x['points'] - y['points'], reverse=True)


class Transformer:
    def __init__(self, db):
        self.client = db

    def get_circle_packing_tree(self, dir_name):
        escaped = '^' + re.escape(dir_name)
        regex = Regex.from_native(re.compile(escaped))
        files = self.client.Hackathon.files.find({
            '_id': regex
        });
        tree = {
            'file_count': 0,
            'name': 'root',
            'children': {},
            'owner': []
        };
        for item in files:
            paths = re.split('[\\\\/]',item['_id'])
            deep_set(tree, paths, item)
        for_display(tree)
        return tree


# client = MongoClient('172.22.117.118')
# optimus = Transformer(client)
# pprint(optimus.get_circle_packing_tree('//package/PackageTools'))