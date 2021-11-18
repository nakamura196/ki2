import requests
import os
import shutil
import json

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)



from bs4 import BeautifulSoup

id = "waseda-" + "ne01_00834"

prefix = "https://archive.wul.waseda.ac.jp/kosho/ne01/ne01_00834"

url = "https://archive.wul.waseda.ac.jp/kosho/ne01/ne01_00834/ne01_00834.html"

res = requests.get(url).text
soup = BeautifulSoup(res, 'html.parser') #2

aas = soup.find_all("a")

index = 1

canvasMap = {}

iiif_prefix = "https://nakamura196.github.io/ki2/iiif/" + id

for a in aas:
    href = a.get("href")

    url = prefix + "/" + href

    if "_p" in href:
        print(href)

        dir = "../data/" + id 
        os.makedirs(dir, exist_ok=True)

        opath = dir + "/" + href

        if not os.path.exists(opath):
            download_img(url, opath)

        import cv2

        im = cv2.imread(opath)

        h, w, c = im.shape

        canvas = {
            "@id": "{}/canvas/p{}".format(iiif_prefix, index),
            "@type": "sc:Canvas",
            "height": h,
            "images": [
                {
                    "@id": "{}/annotation/p{}-image".format(iiif_prefix, index),
                    "@type": "oa:Annotation",
                    "motivation": "sc:painting",
                    "on": "{}/canvas/p{}".format(iiif_prefix, index),
                    "resource": {
                        "@id": url,
                        "@type": "dctypes:Image",
                        "format": "image/jpeg",
                        "height": h,
                        "width": w
                    }
                }
            ],
            "label": "[{}]".format(index),
            "thumbnail": {
                "@id": url.replace("_p", "_s")
            },
            "width": w
        }

        # canvases.append(canvas)
        canvasMap[url] = canvas

        index += 1

canvases = []

for url in sorted(canvasMap):
    canvases.append(canvasMap[url])

manifest = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": "{}/manifest.json".format(iiif_prefix),
    "@type": "sc:Manifest",
    "attribution": "早稲田大学",
    "label": "{}".format(id),
    "metadata": [],
    "sequences": [
        {
            "@id": "{}/sequence/normal".format(iiif_prefix),
            "@type": "sc:Sequence",
            "canvases": canvases
        }
    ]
}



opath2 = "../../docs/iiif/" + id + "/manifest.json"

os.makedirs(os.path.dirname(opath2), exist_ok=True)

with open(opath2, mode='wt', encoding='utf-8') as file:
            json.dump(manifest, file, ensure_ascii=False, indent=2)
