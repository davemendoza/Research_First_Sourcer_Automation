import json,datetime
OUTPUT="outputs/capability_overlap_registry.json"
def generate():
    data={"generated":datetime.datetime.utcnow().isoformat(),"overlap":{}}
    with open(OUTPUT,"w") as f: json.dump(data,f,indent=2)
if __name__=="__main__": generate()
