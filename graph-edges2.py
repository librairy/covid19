import requests
import csv
import pysolr

with open('edges.csv', 'r') as input:
    spamreader = csv.reader(input, delimiter=',', quotechar='"')
    next(input, None)
    with open('edges2.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['source', 'target', 'score', 'weight'])

        for row in spamreader:
            source = row[0]
            target = row[1]
            score = float(row[2])
            weight = int(10000.0*score)
            filewriter.writerow([source, target, score, weight])
            print(source,target,score,weight)
