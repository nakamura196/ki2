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

def main(id):
    # id = "waseda-ne01_00834"

    git_prefix = "https://nakamura196.github.io/ki2"

    curation_uri = git_prefix + "/curation/{}.json".format(id)

    manifest = git_prefix + "/iiif/{}/manifest.json".format(id)


    dir = "data/" + id
    odir = "data/json/" + id

    os.makedirs(dir, exist_ok=True)
    os.makedirs(odir, exist_ok=True)

    # df = requests.get(manifest).json()

    with open("../docs/iiif/{}/manifest.json".format(id), mode='rt', encoding='utf-8') as file:

        # 辞書オブジェクト(dictionary)を取得
        df = json.load(file)

    index = 0

    DETECTION_URL = "http://app.ldas.jp:5003/v1/predict"

    members = []

    canvases = df["sequences"][0]["canvases"]

    for canvas in canvases:
        image = canvas["images"][0]["resource"]["@id"]

        filename = image.split("/")[-1]

        path = "data/" + id + "/" + filename

        print(index, len(canvases), image)

        if not os.path.exists(path):
            try:
                download_img(image, path)
            except Exception as e:
                print(e)
                continue

        opath = odir + "/" + str(index).zfill(5) + ".json"

        if not os.path.exists(opath):

            image_data = open(path, "rb").read()

            response = requests.post(DETECTION_URL, files={"image": image_data}).json()

            with open(opath, mode='wt', encoding='utf-8') as file:
                json.dump(response, file, ensure_ascii=False, indent=2)

        r = 1 # canvas["width"] / 600

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
                    "label": "aaa",
                    "metadata" : [
                        {
                            "label" : "confidence",
                            "value" : item["confidence"]
                        }
                    ]
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


import glob

files = glob.glob("data/waseda-*")

index = 0

for file in files:

    index += 1

    print(index, len(files))

    id = file.split("/")[-1]

    main(id)

