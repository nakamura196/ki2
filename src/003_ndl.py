import requests
import os
import shutil
import json
import pandas as pd

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

git_prefix = "https://nakamura196.github.io/ki2"

def main(id):

    curation_uri = git_prefix + "/curation/{}.json".format(id)

    '''
    ndl_id = "1286722"

    manifest = "https://www.dl.ndl.go.jp/api/iiif/"+ndl_id+"/manifest.json"


    id = "dignl-" + ndl_id

    '''

    '''

    manifest = "https://lib.digitalnc.org/nanna/iiif/106447/manifest"
    id = "digitalnc-" + "106447"

    '''

    # id = "dignl-11223490"

    manifest = "https://www.dl.ndl.go.jp/api/iiif/{}/manifest.json".format(id)
    
    id = "dignl-" + id

    df = requests.get(manifest).json()
    if "sequences" not in df:
        return

    dir = "data/" + id
    odir = "data/json/" + id

    os.makedirs(dir, exist_ok=True)
    os.makedirs(odir, exist_ok=True)

    

    index = 0

    DETECTION_URL = "http://app.ldas.jp:5003/v1/predict"

    members = []

    for canvas in df["sequences"][0]["canvases"]:
        image = canvas["images"][0]["resource"]["service"]["@id"] + "/full/600,/0/default.jpg"

        path = "data/" + id + "/" + str(index).zfill(5) + ".jpg"

        print(path, image)

        if not os.path.exists(path):
            download_img(image, path)

        opath = odir + "/" + str(index).zfill(5) + ".json"

        if not os.path.exists(opath):

            image_data = open(path, "rb").read()

            response = requests.post(DETECTION_URL, files={"image": image_data}).json()

            with open(opath, mode='wt', encoding='utf-8') as file:
                json.dump(response, file, ensure_ascii=False, indent=2)

        r = canvas["width"] / 600

        with open(opath, mode='rt', encoding='utf-8') as file:

            # 辞書オブジェクト(dictionary)を取得
            df = json.load(file)

            for item in df:
                x = int(item["xmin"] * r)
                y = int(item["ymin"] * r)
                w = int((item["xmax"] - item["xmin"]) * r)
                h = int((item["ymax"] - item["ymin"]) * r)

                member_id = canvas["@id"] + "#xywh={},{},{},{}".format(x, y, w, h)

                members.append({
                    "@id": member_id,
                    "@type": "sc:Canvas",
                    "label": "[{}]".format(index + 1),
                    "metadata" : [
                        {
                            "label" : "confidence",
                            "value" : item["confidence"]
                        }
                    ],
                    "thumbnail" : canvas["images"][0]["resource"]["service"]["@id"] + "/{},{},{},{}/200,/0/default.jpg".format(x, y, w, h)
                })

        index += 1


    curation = {
        "@context": [
            "http://iiif.io/api/presentation/2/context.json",
            "http://codh.rois.ac.jp/iiif/curation/1/context.json"
        ],
        "@id": curation_uri,
        "@type": "cr:Curation",
        "label": "",
        "selections": [
            {
                "@id": "{}/range".format(curation_uri),
                "@type": "sc:Range",
                "label": "",
                "members": members,
                "within": {
                    "@id": manifest,
                    "@type": "sc:Manifest",
                    "label": ""
                }
            }
        ]
    }

    opath2 = "../docs/curation/" + id + ".json"

    with open(opath2, mode='wt', encoding='utf-8') as file:
                json.dump(curation, file, ensure_ascii=False, indent=2)

df = pd.read_csv('ndl/list.csv')

for index, row in df.iterrows():
    print("index", index)
    main(str(row["id"]))