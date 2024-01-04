from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor
import json


def set_config_elsevir():
    ## Load configuration
    con_file = open("scopus/config_elsevir.json")
    config = json.load(con_file)
    con_file.close()

    ## Initialize client
    client = ElsClient(config['apikey'])
    client.inst_token = config['insttoken']
    return client

def process_record(_client:ElsClient , scopus_id):
    author = ElsAuthor(author_id=scopus_id)
    data = author.read_metrics(_client)
    return data, author.data
