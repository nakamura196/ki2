import requests
import os
import shutil
import json
import glob

files = glob.glob("../docs/curation/*.json")

attrs = {
    "dignl" : "国立国会図書館",
    "waseda" : "早稲田大学",
    "digitalnc" : "その他"
}

indexes = []

tags = {}

files2 = glob.glob("tag/*.json")

for f2 in files2:
    id = f2.split("/")[-1].split(".")[0]
    with open(f2, mode='rt', encoding='utf-8') as file:

        # 辞書オブジェクト(dictionary)を取得
        df = json.load(file)

        for key in df:
            arr = df[key]
            values = []
            for value in arr:
                values.append(value["tag"])
            tags[id+"-"+key] = values

for f in files:

    id = f.split("/")[-1].split(".")[0]

    with open(f, mode='rt', encoding='utf-8') as file:

        # 辞書オブジェクト(dictionary)を取得
        df = json.load(file)

        members = df["selections"][0]["members"]

        index = 0
        for member in members:

            item = {}

            objectID = id + "-" + str(index).zfill(5)

            item["objectID"] = objectID
            item["label"] = objectID
            if "thumbnail" in member:
                item["thumbnail"] = member["thumbnail"]

            if objectID in tags:
                item["tags"] = tags[objectID]

            prefix = id.split("-")[0]

            item["source"] = attrs[prefix]

            indexes.append(item)

            index += 1

with open("../../poster/static/data/index.json", mode='wt', encoding='utf-8') as file:
    json.dump(indexes, file, ensure_ascii=False, indent=2)

