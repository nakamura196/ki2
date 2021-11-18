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

'''
ndl_id = "1286722"

manifest = "https://www.dl.ndl.go.jp/api/iiif/"+ndl_id+"/manifest.json"


id = "dignl-" + ndl_id

'''

from bs4 import BeautifulSoup

id = "waseda-" + "ne01_00834"

prefix = "https://archive.wul.waseda.ac.jp/kosho/ne01/ne01_00834"

url = "https://archive.wul.waseda.ac.jp/kosho/ne01/ne01_00834/ne01_00834.html"

res = requests.get(url).text
soup = BeautifulSoup(res, 'html.parser') #2

aas = soup.find_all("a")

index = 1

canvasMap = {}



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

        print(h, w)

        canvas = {
            "@id": "https://nakamura196.github.io/hi/data/02/01/{}.json/canvas/p{}".format(id, index),
            "@type": "sc:Canvas",
            "height": h,
            "images": [
                {
                    "@id": "https://nakamura196.github.io/hi/data/02/01/{}.json/annotation/p{}-image".format(id, index),
                    "@type": "oa:Annotation",
                    "motivation": "sc:painting",
                    "on": "https://nakamura196.github.io/hi/data/02/01/{}.json/canvas/p{}".format(id, index),
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
    "@id": "https://nakamura196.github.io/hi/data/02/01/{}.json".format(id),
    "@type": "sc:Manifest",
    "attribution": "Historiographical Institute The University of Tokyo 東京大学史料編纂所",
    "description": "仁和 3年 8月～寛平3年12月",
    "label": "『大日本史料』・1編・1",
    "license": "http://creativecommons.org/licenses/by-nc-sa/4.0/",
    "logo": "http://www.hi.u-tokyo.ac.jp/favicon.ico",
    "metadata": [],
    "sequences": [
        {
            "@id": "https://nakamura196.github.io/hi/data/02/01/{}.json/sequence/normal".format(id),
            "@type": "sc:Sequence",
            "canvases": canvases
        }
    ]
}



opath2 = "../../docs/iiif/" + id + "/manifest.json"

os.makedirs(os.path.dirname(opath2), exist_ok=True)

with open(opath2, mode='wt', encoding='utf-8') as file:
            json.dump(manifest, file, ensure_ascii=False, indent=2)
