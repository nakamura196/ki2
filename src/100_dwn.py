import requests
import os
import shutil
import json
import glob

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

files = glob.glob("../docs/curation/dignl-*.json")

for f in files:

    id = f.split("/")[-1].split(".")[0]

    with open(f, mode='rt', encoding='utf-8') as file:

        # 辞書オブジェクト(dictionary)を取得
        df = json.load(file)

        members = df["selections"][0]["members"]

        index = 0
        for member in members:
            url = member["thumbnail"].replace("200,", "600,")

            opath = "files/" + id + "/" + str(index).zfill(5) + ".jpg"

            if not os.path.exists(opath):
                os.makedirs(os.path.dirname(opath), exist_ok=True)

                download_img(url, opath)

            index += 1
