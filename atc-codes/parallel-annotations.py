#!/usr/bin/env python3
# docker run -d -p 6200:5000 librairy/bio-nlp:latest
import tarfile
import urllib.request
import json
import requests
import pysolr
import os
import multiprocessing as mp
from datetime import datetime
import time

initial = 0

# librAIry Bio-NLP Endpoint
#API_ENDPOINT = "http://localhost:5000/bio-nlp/drugs"
API_ENDPOINT = "http://localhost:6200/bio-nlp/drugs"

# Setup a Solr instance. The timeout is optional.
solr = pysolr.Solr('http://pcalleja.oeg-upm.net/8983/solr/covid-sentences', timeout=2)

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

def get_document(annotated_sentence):
    if (not 'text_t' in annotated_sentence):
        return annotated_sentence
    codes = {}
    available_codes = [0,1,2,3,4,5]
    for code in available_codes:
        codes[code] = []        
    sentence = annotated_sentence['text_t']
    for drug in get_drugs(sentence):
        print(drug,"found")
        if ("level" in drug) and ("atc_code" in drug):
            level = int(drug["level"])
            codes[level].append(str(drug["atc_code"]))          
    for code in available_codes:
        if (len(codes[code]) > 0):
            annotated_sentence['bionlp_atc'+str(code)+'_t']= " ".join(codes[code])
    #print(annotated_sentence)
    return annotated_sentence


pool = mp.Pool(4)

counter = 0
completed = False
window_size=100
cursor = "*"
while (not completed):
    old_counter = counter
    solr_query="!bionlp_atc1_t:[* TO *] AND !bionlp_atc2_t:[* TO *] AND !bionlp_atc3_t:[* TO *] AND !bionlp_atc4_t:[* TO *] AND !bionlp_atc5_t:[* TO *]"
    try:
        sentences = solr.search(q=solr_query,rows=window_size,cursorMark=cursor,sort="id asc")
        cursor = sentences.nextCursorMark
        counter += len(sentences)
        documents = pool.map(get_document, sentences)
        solr.add(documents)
        solr.commit()
        print("[",datetime.now(),"] solr index updated! -",counter)
        if (old_counter == counter):
            print("done!")
            break
    except:
        print("Solr query error. Wait for 5secs..")
        time.sleep(5.0)

print(counter,"sentences successfully annotated with ATC-Codes")
pool.close()
