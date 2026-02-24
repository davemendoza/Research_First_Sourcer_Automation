import json, os, datetime
OUTPUT="outputs/capability_registry.json"
def generate():
    data={"generated":datetime.datetime.utcnow().isoformat(),"capabilities":{}}
    with open(OUTPUT,"w") as f: json.dump(data,f,indent=2)
if __name__=="__main__": generate()
