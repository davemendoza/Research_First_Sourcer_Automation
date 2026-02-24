import json,datetime
OUTPUT="outputs/succession_risk_registry.json"
def generate():
    data={"generated":datetime.datetime.utcnow().isoformat(),"risk_scores":{}}
    with open(OUTPUT,"w") as f: json.dump(data,f,indent=2)
if __name__=="__main__": generate()
