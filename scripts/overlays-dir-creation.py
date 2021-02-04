import yaml, os, shutil, sys
def create_basic_struct():
  os.makedirs("kustomize/overlays/backend/releases/", exist_ok=True)
  os.makedirs("kustomize/overlays/backend/features/", exist_ok=True)
  os.makedirs("kustomize/overlays/frontend/releases/", exist_ok=True)
  os.makedirs("kustomize/overlays/frontend/features/", exist_ok=True)
    
def create_kustomization(branch, list_branch, final_folder, tier, app_name):
  k = {}
  k["kind"] = "Kustomization"
  k["apiVersion"] = "kustomize.config.k8s.io/v1beta1"
  if branch == "master":
    k["resources"] = ["../../base"]
    k["namespace"] = app_name+"-prod"
  else: 
    k["resources"] = ["../../../../base"]
    k["namespace"] = app_name+"-"+tier+"-"+list_branch[0]+"-"+list_branch[1]
    
  open(final_folder+"/kustomization.yaml", "x")
  with open(final_folder+"/kustomization.yaml", "w") as file:
    yaml.dump(k, file)

def main():
  branch = os.environ["CODE_BRANCH"]
  tier = os.environ["TIER"]
  app_name = os.environ["APP_NAME"]
  prod_input_master = os.environ["PROD_INPUT_MASTER"]
  list_branch = branch.split("/")
  
  create_basic_struct()

  if(len(list_branch) == 1 and branch == "master"):
    overlays_folder = "kustomize/overlays/"
    final_folder = overlays_folder+"prod/"
    #create_specific_struct("prod", "kustomize/overlays", folder)
    if "prod" in os.listdir(overlays_folder):
      if (prod_input_master == "backend" and tier == "frontend") or (prod_input_master == "frontend" and tier == "backend"):
        return
      #delete path
      shutil.rmtree(final_folder, ignore_errors=True)
    #create path
    os.makedirs(final_folder, exist_ok= True)
      
  else:
    overlays_folder = "kustomize/overlays/"+tier+"/"
    if(len(list_branch) == 2 and "features" == list_branch[0] and len(list_branch[1].strip())>0):
      features_folder = overlays_folder+"features/"
      final_folder = features_folder+list_branch[-1]+"/"
      #create_specific_struct(list_branch[-1], overlays, folder, list_branch[-1])
      if list_branch[-1] in os.listdir(features_folder):
        #delete path
        shutil.rmtree(final_folder, ignore_errors=True)
      #create path
      os.makedirs(final_folder, exist_ok= True)
    elif(len(list_branch) == 2 and "releases" == list_branch[0] and len(list_branch[1].strip())>0):
      releases_folder = overlays_folder+ "releases/"
      final_folder = releases_folder+list_branch[-1]+"/"
      #create_specific_struct(list_branc[-1], overlays, folder, list_branch[-1])
      if list_branch[-1] in os.listdir(releases_folder):
        #delete path
        shutil.rmtree(final_folder, ignore_errors=True)
      #create path
      os.makedirs(final_folder, exist_ok= True)
    else:
      sys.exit("Branch is not correct!")

  #create kustomization.yaml
  create_kustomization(branch, list_branch, final_folder, tier, app_name)


if __name__ == '__main__':
    main()
