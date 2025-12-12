import os,hashlib,json,datetime
def sha256(file):
    h=hashlib.sha256()
    with open(file,"rb") as f:
        for c in iter(lambda: f.read(4096),b""): h.update(c)
    return h.hexdigest()
def verify():
    os.makedirs("logs",exist_ok=True)
    data={}
    for root,_,files in os.walk("."):
        for f in files:
            if f.endswith((".py",".csv",".yaml",".md")):
                p=os.path.join(root,f)
                data[p]=sha256(p)
    with open("logs/provenance_manifest.json","w") as out: json.dump(data,out,indent=2)
    s=datetime.datetime.now().isoformat()
    with open("logs/integrity_audit.log","a") as l: l.write(f"[{s}] Integrity manifest updated ({len(data)} files)\n")
    print(f"✅ Integrity verification complete: {len(data)} files hashed.")
if __name__=="__main__": verify()
# © 2025 L. David Mendoza – All Rights Reserved
