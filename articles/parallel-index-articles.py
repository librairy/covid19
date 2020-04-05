#!/usr/bin/env python3
import tarfile
import urllib.request
import json
import requests
import pysolr
import os
import multiprocessing as mp
from datetime import datetime


def get_document(file_url):
    with open(file_url) as f:
      license = file_url.split("/")[4]       
      data = json.load(f)
      document = {}
      metadata = data['metadata']
      document['id'] = data['paper_id']
      results = solr.search("id:"+document['id'])
      if (len(results) > 0):
            print("Found",document["id"])
            return results      
      document['name_s'] = data['metadata']['title']
      if (("abstract" in data) and (len(data['abstract']) > 0)):
          document['abstract_t']= data['abstract'][0]['text']
      paragraphs = []
      for paragraph in data['body_text']:
          if (len(paragraphs) > 100):
              break
          paragraphs.append(paragraph['text'])
      document['txt_t']= " ".join(paragraphs)
      document["source_s"] = license
      print("-", document["id"], document["name_s"])
      return document


# Articles
directories = [
    ("/Users/cbadenes/Downloads/custom_license/pdf_json","custom_license"),
    ("/Users/cbadenes/Downloads/custom_license/pmc_json","custom_license"),
    ("/Users/cbadenes/Downloads/comm_use_subset/pmc_json","commercial_use"),
    ("/Users/cbadenes/Downloads/comm_use_subset/pdf_json","commercial_use"),
    ("/Users/cbadenes/Downloads/biorxiv_medrxiv/pdf_json","biorxiv"),
    ("/Users/cbadenes/Downloads/noncomm_use_subset/pmc_json","noncommercial_use"),
    ("/Users/cbadenes/Downloads/noncomm_use_subset/pdf_json","noncommercial_use")
]

solr = pysolr.Solr('https://librairy.linkeddata.es/data/covid', timeout=10)
pool = mp.Pool(4)
        
for directory in directories:
    print("Indexing directory", directory)
    directory_path = directory[0]
    files = os.listdir(directory_path)
    min = 0
    max = 0
    incr = 500
    counter = 0
    while(max < len(files)):
        min = counter
        max = min + incr
        if (max > len(files)):
            max = len(files)
        documents = pool.map(get_document, [directory_path + "/" + file for file in files[min:max]])
        commit_documents = [doc for doc in documents if 'name_s' in doc]
        print("[",datetime.now(),"]","indexing",len(commit_documents)," docs...")
        try:
            solr.add(commit_documents)
            solr.commit()
        except:
            print("Solr query error. Wait for 5secs..")
            time.sleep(5.0)
            solr.commit()
        counter=max
        break
    
    
print(counter,"docs added")
pool.close()
