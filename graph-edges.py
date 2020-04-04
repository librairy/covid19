import requests
import csv
import pysolr


with open('edges.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)

    response = requests.get("https://librairy.linkeddata.es/covid19-model/topics")

    filewriter.writerow(['source', 'target', 'score'])

    nodes = []
    for topic in response.json():
        source = topic['id']
        print("#####",source)
        response_neighbours = requests.get("https://librairy.linkeddata.es/covid19-model/topics/"+str(source)+"/neighbours?max=4000")
        for neighbour in response_neighbours.json():
            target = neighbour["id"]
            score = neighbour["score"]
            if (score > 0.001):
                filewriter.writerow([source, target, score])
                print(source,target,score)
