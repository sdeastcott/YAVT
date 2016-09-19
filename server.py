import os
import tempfile
from pymongo import MongoClient
from src.Transformer import Transformer
from bottle import run, get, post, hook, request, response, route, static_file


@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@get('/getVersion')
def get_version():
    response.content_type = 'application/json'
    return {"name": "Domain Expert", "version": version}

@route("/runDomainExpert", method="OPTIONS")
def validate():
    return ""

@get('/')
def get_index_file():
    return static_file('index.html', os.getcwd() + '/views' )

@get('/testData.json')
def get_data():
    client = MongoClient('<ip address of mongo server>')
    optimus = Transformer(client)
    return optimus.get_circle_packing_tree('//full/perforce/path/here')

@post('/runDomainExpert')
def run_perforce_domain_tool():
    response.content_type = 'application/json'
    return {"results": "", "error": ""}

if __name__ == "__main__":
    run(host="0.0.0.0", port = 8090)
