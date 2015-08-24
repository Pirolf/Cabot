from ImageClassifier import ImageClassifier
import json
import sys

RESULT_FILE_NAME = 'result.json'
if len(sys.argv) != 2:
    exit()

imageUrl = str(sys.argv[1])

classifier = ImageClassifier(**ImageClassifier.default_args)
classifier.net.forward()
result = classifier.classify_url(imageUrl)

#write to json
jsonResult = json.dumps(result[2])
resultFile = open(RESULT_FILE_NAME, 'w+')
resultFile.write(jsonResult)
resultFile.close()
