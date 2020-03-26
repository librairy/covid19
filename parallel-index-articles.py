#!/usr/bin/env python3
import tarfile
import urllib.request
import json
import requests
import pysolr
import os
import multiprocessing as mp
from datetime import datetime

initial = 0

# librAIry Bio-NLP Endpoint
#API_ENDPOINT = "http://localhost:5000/bio-nlp/drugs"
API_ENDPOINT = "http://localhost:6200/bio-nlp/drugs"

# Articles
#directory_path = "/Users/cbadenes/Downloads/noncomm_use_subset"
#directory_path = "/Users/cbadenes/Downloads/covid19/comm_use_subset"
directory_path = "/home/cbadenes/covid19/custom_license"

# Setup a Solr instance. The timeout is optional.
#solr = pysolr.Solr('https://librairy.linkeddata.es/data/covid', timeout=10)
solr = pysolr.Solr('https://localhost:8983/solr/covid', timeout=10)

def get_drugs(text):
    data = {}
    data['text']=text
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url = API_ENDPOINT, data = json.dumps(data), headers=headers)
    #convert response to json format
    try:
        drugs =  response.json()
        return drugs
    except:
        print("No response from get_drugs")
        return []

def get_document(file_url,doc_type="commercial_use"):
    with open(directory_path + "/" + file_url) as f:
      data = json.load(f)
      document = {}
      codes4 = []
      codes5 = []
      metadata = data['metadata']
      document['name_s'] = data['metadata']['title']
      document['id'] = data['paper_id']
      if (("abstract" in data) and (len(data['abstract']) > 0)):
          document['abstract_t']= data['abstract'][0]['text']
          for drug in get_drugs(document['abstract_t']):
              if ("level" in drug):
                  if (drug["level"] == 4) and ("atc_code" in drug):
                      codes4.append(drug["atc_code"])
                  elif (drug["level"] == 5):
                      if ("atc_parent" in drug):
                          codes4.append(drug["atc_parent"])
                      if ("atc_code" in drug):
                          codes5.append(drug["atc_code"])
      paragraphs = []
      for paragraph in data['body_text']:
          if (len(paragraphs) > 100):
              break
          paragraph_text = paragraph['text']
          for drug in get_drugs(paragraph_text):
              if ("level" in drug):
                  if (drug["level"] == 4 and "atc_code" in drug):
                      codes4.append(drug["atc_code"])
                  elif (drug["level"] == 5):
                      if ("atc_parent" in drug):
                          codes4.append(drug["atc_parent"])
                      if ("atc_code" in drug):
                          codes5.append(drug["atc_code"])
          paragraphs.append(paragraph_text)
      document['labels4_t']= " ".join(list(set(codes4)))
      document['labels5_t']= " ".join(list(set(codes5)))
      document['txt_t']= " ".join(paragraphs)
      document["source_s"] = doc_type
      print("-", document["name_s"])
      return document

pool = mp.Pool(8)

counter = 0
files = os.listdir(directory_path)
min = 0
max = 0
incr = 50
while(max < len(files)):
    if (counter < initial):
        counter += 1
        continue
    min = counter
    max = min + incr
    if (max > len(files)):
        max = len(files)
    documents = pool.map(get_document, files[min:max])
    solr.add(documents)
    solr.commit()
    print(min,"-", max, "commit","[",print(datetime.now()),"]")
    counter=max


#solr.add(documents)
#solr.commit()
print(counter,"docs added")
pool.close()
