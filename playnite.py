import json
import os
import subprocess
print(os.getenv('APPDATA'))

class playnite:
    def __init__(self):
        self.source = "playnite"
        self.program = os.path.join(os.getcwd(), "playnite_dump", "PlayniteDump.exe")
        self.hltb = os.path.join(os.getenv('APPDATA'), """Playnite\ExtensionsData\e08cd51f-9c9a-4ee3-a094-fde03b55492f\HowLongToBeat""")
  
    def parse(self):
        result = subprocess.check_output([self.program], shell=True).decode("utf-8").splitlines()
        data = []
        for line in result:
            try:
                with open(os.path.join(self.hltb, line + ".json"), "r", encoding="utf-8") as f:
                    obj = json.load(f)
                    item = obj["Items"][0]
                    data.append({   "name": item["Name"],
                                    "source": self.source,
                                    "url": item["Url"],
                                    "type": "game",
                                    "length": item["GameHltbData"]["MainExtraClassic"] / 3600 or item["GameHltbData"]["MainStoryClassic"] / 3600
                                })
            except:
                pass
        return data

    def scrape(self):
        return self.parse()