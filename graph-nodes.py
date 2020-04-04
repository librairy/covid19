import requests
import csv
import pysolr

solr = pysolr.Solr('https://librairy.linkeddata.es/solr/atc', timeout=10)

with open('nodes.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)

    response = requests.get("https://librairy.linkeddata.es/covid19-model/topics")

    filewriter.writerow(['id', 'code', 'name', 'description', 'url'])

    nodes = []
    for topic in response.json():
        id = topic['id']
        code = topic['name']
        description = topic['description']
        url = "https://librairy.linkeddata.es/covid19-model/topics/"+str(topic['id'])+"/words"

        results = solr.search("code_s:"+code)
        name = ""
        for result in results:
            name = result['label_t']

        filewriter.writerow([id, code, name, description, url])
        print(id, code, name, description, url)
