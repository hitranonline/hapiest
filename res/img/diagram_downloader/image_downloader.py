import urllib.request

url_prefix = "https://cactus.nci.nih.gov/chemical/structure/"
url_suffix = "/image?width=500&height=500&linewidth=4&symbolfontsize=32"
path_prefix = "../molecules"
import os
if not os.path.isfile("../../../data/.cache/.molm"):
    print("Run hapi with the data directory set to 'data' and try again.")
    os._exit(-1)
import json
text = ''
with open('../../../data/.cache/.molm', 'r') as file:
    text = file.read()
parsed = json.loads(text)
if 'cached' in parsed:
    parsed = json.loads(parsed['cached'])

for molecule in parsed:
        inchi = molecule['inchi']
        #print(inchi)
        #print(int(filenum))
        inchifixed = inchi.replace('(', '%28').replace(')', '%29')
        #print(inchifixed)
        url = url_prefix + inchifixed + url_suffix
        print(url)
        #print(url)
        filename = str(molecule['ordinary_formula']) + ".gif"
        path = path_prefix + "/" + filename
        try:
            urllib.request.urlretrieve(url, path)
        except:
            print("Failed to retreive {}".format(filename))