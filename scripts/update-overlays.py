import yaml, os, shutil
#from yaml_update import yaml_updates
#from kind_name import getKindName

#get the metadata name of the k8s object kept in analysis
#Questo metodo si basa sul fatto che possa essere updatato, che sia per backend,frontend o db, solo o il 
#Deployment o il Service. Quindi nel dubbio si salva il metadata name di ambedue gli oggetti, affinchè siano 
#identificati in modo univoco

def getMetadataName(tierValue):
    kind_name = {}
    for filename in os.listdir("kustomize/base/"):
        with open(os.path.join("kustomize/base/", filename)) as file:
            input = yaml.load(file, Loader=yaml.FullLoader)
        if input["kind"] == "Deployment":
            if input["spec"]["template"]["metadata"]["labels"]["tier"] == tierValue:
                kind_name["deployment"] = input["metadata"]["name"]
        elif input["kind"] == "Service":
            if input["spec"]["selector"]["tier"] == tierValue:
                kind_name["service"] = input["metadata"]["name"]
    return kind_name

def yaml_updates(input_data, dir_path, kind_name, tier):
    for x in input_data:
        if(x["type"] == "deployment"):
            x.pop("type")
            update_deployment(x, kind_name["deployment"], dir_path, tier)
        elif(x["type"] == "service"):
            x.pop("type")
            update_service(x, kind_name["service"], dir_path, tier)



def update_deployment(values, kind_name, dir_path, tier):
    for k,v  in values.items():
        if(k == "replicas" or k == "secrets"):
            patch_kustomization(dir_path, k, v, kind_name, tier, "deployment")

def update_service(values, kind_name, dir_path, tier):
    for k,v  in values.items():
        if(k == "port"):
            patch_kustomization(dir_path, k, v, kind_name, tier, "service")


def patch_kustomization(dir_path, key, value, kind_name, tier, kind_type):
    #il file kustomization c'è sicuramente perchè è stato creato con lo script precedente
    kustomize_path = dir_path + "kustomization.yaml"
    patch_file_name = tier+"_"+kind_name+"_"+kind_type+"_patch.yaml"
    with open(kustomize_path) as file:
            kustomization = yaml.load(file, Loader=yaml.FullLoader)
    
    entry = {"target": {"name" : kind_name, "labelSelector" : "tier="+tier}, "path" : patch_file_name}

    if "patches" not in kustomization.keys():
        kustomization["patches"] = [entry]
        #aggiungo scrivendo, la key patch
        with open(kustomize_path, "w") as file:
            yaml.dump(kustomization, file)
    else:
        #vuol dire che la entry patch esiste, ma non è detto che esista nella sua lista, il list_value necessario
        for e in kustomization["patches"]:
            if e["path"] == patch_file_name:
                kustomization["patches"].remove(e)
                break
        kustomization["patches"].append(entry)
        with open(kustomize_path, "w") as file:
            yaml.dump(kustomization, file)
    
    #adesso devo aggiungere il file patch.yaml, se non esiste
    if patch_file_name not in os.listdir(dir_path):
        open(dir_path+patch_file_name, "x")
        patch = []
    else:
        with open(dir_path+patch_file_name) as file:
            patch = yaml.load(file, Loader=yaml.FullLoader)

    if(key == "replicas"):
        if(patch == []):
            patch = [{"op" : "add", "path" : "/spec/replicas", "value" : value}]
        else:
            found = False
            for ele in patch:
                if(ele["path"] == "/spec/replicas"):
                    ele["value"] = value
                    found = True
                    break
            if(found == False):
                patch.append(dict({"op" : "add", "path" : "/spec/replicas", "value" : value}))
        with open(dir_path+patch_file_name, "w") as file:
            yaml.dump(patch, file)
    elif(key == "port"):
        if(patch == []):
            patch = [{"op" : "add", "path" : "/spec/ports/0/port", "value" : value}]
        else:
            for ele in patch:
                found = False
                if(ele["path"] == "/spec/ports/0/port"):
                    ele["value"] = value
                    found = True
                    break
            if(found == False):
                patch.append(dict({"op" : "add", "path" : "/spec/ports/0/port", "value" : value}))
        with open(dir_path+patch_file_name, "w") as file:
            yaml.dump(patch, file)

    elif(key == "secrets"):
        new_value = secret_generator(value, kustomize_path, tier, kind_name)
        if(patch == []):
            patch = [{"op" : "add", "path" : "/spec/template/spec/containers/0/env", "value" : new_value}]
        else:
            for ele in patch:
                found = False
                if(ele["path"] == "/spec/template/spec/containers/0/env"):
                    ele["value"] = new_value
                    found = True
                    break
            if(found == False):
                patch.append(dict({"op" : "add", "path" : "/spec/template/spec/containers/0/env", "value" : new_value}))
        with open(dir_path+patch_file_name, "w") as file:
            yaml.dump(patch, file)
    

def secret_generator(secrets, kustomization_path, tier, kind_name):
    #1)controlla se esiste la entry in kustomization e se non esiste, aggiungila
    #2)ogni elemento della lista, deve avere un nome, che farò in modo tale sia simile e matchabile in modo standard, con il codice 
    with open(kustomization_path) as file:
            kustomization = yaml.load(file, Loader=yaml.FullLoader)
    if "secretGenerator" in kustomization.keys():
        kustomization.pop("secretGenerator", None)

    literals = []
    for ele in secrets:
        for x,y in ele.items():
            literals.append(x+"="+y)
    kustomization["secretGenerator"] = [{"name" : tier+"-"+kind_name , "literals" : literals}]
    with open(kustomization_path, "w") as file:
        yaml.dump(kustomization, file)
    
    valueToReturn = []

    for val in secrets:
        for x,y in val.items():
            valueToReturn.append({"name": x, "valueFrom": { "secretKeyRef": { "name" : tier+"-"+kind_name , "key" : x}}})
    return valueToReturn



def main():

    with open("./input.yaml") as file:
        input = yaml.load(file, Loader=yaml.FullLoader)

    tier = os.environ["TIER"]
    prod_input_master = os.environ["PROD_INPUT_MASTER"]

    if input["branch"] == "master":
        if (prod_input_master == "backend" and tier == "frontend") or (prod_input_master == "frontend" and tier == "backend"):
            return

    

    if(input["branch"] == "master"):
        dir_path = "kustomize/overlays/prod/"
    else:
        dir_path = "kustomize/overlays/"+tier+"/"+input['branch']+"/"
    input.pop('branch')

    be = None
    fe = None
    db = None

    for k,v in input.items():
        if k == "backend":
            be = v
        elif k == "frontend":
            fe = v
        elif k == "db":
            db = v
    
    if be != None:
        kind_name = getMetadataName("backend")
        #Update vales
        yaml_updates(be, dir_path, kind_name, "backend")
    if fe != None:
        kind_name = getMetadataName("frontend")
        #Update vales
        yaml_updates(fe, dir_path, kind_name, "frontend")
    if db != None:
        kind_name = getMetadataName("db")
        #Update vales
        yaml_updates(db, dir_path, kind_name, "db")
    

if __name__ == '__main__':
    main()
