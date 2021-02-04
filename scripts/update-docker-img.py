import yaml, os

def main():
  
  tier = os.environ["TIER"]
  code_branch = os.environ["CODE_BRANCH"]
  user_dockerhub = os.environ["DOCKER_USER"]  
  repo_name_frontend_dockerhub = os.environ["DOCKER_FRONTEND_REPO"]
  repo_name_backend_dockerhub = os.environ["DOCKER_BACKEND_REPO"]
  image_tag = os.environ["DOCKER_IMAGE_TAG"]

  if "master" in code_branch:
    kustomization_path = "kustomize/overlays/prod/kustomization.yaml"
  else: 
    kustomization_path = "kustomize/overlays/"+tier+"/"+code_branch+"/kustomization.yaml"

  for filename in os.listdir("kustomize/base/"):
          with open(os.path.join("kustomize/base/", filename)) as file:
              f = yaml.load(file, Loader=yaml.FullLoader)
          if f["kind"] == "Deployment":
              if f["spec"]["template"]["metadata"]["labels"]["tier"] == "frontend":
                imageNameFrontend = f["spec"]["template"]["spec"]["containers"][0]["name"]
              elif f["spec"]["template"]["metadata"]["labels"]["tier"] == "backend":
                imageNameBackend = f["spec"]["template"]["spec"]["containers"][0]["name"]
  with open(kustomization_path) as file:
      kustomization = yaml.load(file, Loader=yaml.FullLoader)
  
  if "master" in code_branch:
    #done for trigger sync by argocd, since the tag-img is composed by sha of commit, that is 
    #always different
    if tier == "backend":
      entryBackend = {"name" : imageNameBackend, "newName" : user_dockerhub+"/"+repo_name_backend_dockerhub, "newTag" : image_tag}
      entryFrontend = {"name" : imageNameFrontend, "newName" : user_dockerhub+"/"+repo_name_frontend_dockerhub, "newTag" : "latest-prod"}
    else:
      entryBackend = {"name" : imageNameBackend, "newName" : user_dockerhub+"/"+repo_name_backend_dockerhub, "newTag" : "latest-prod"}
      entryFrontend = {"name" : imageNameFrontend, "newName" : user_dockerhub+"/"+repo_name_frontend_dockerhub, "newTag" : image_tag}
  else:

    if(tier == "backend"):
      imageTagFrontend = ""
      entryBackend = {"name" : imageNameBackend, "newName" : user_dockerhub+"/"+repo_name_backend_dockerhub, "newTag" : image_tag}
      with open("./input.yaml") as file:
        input = yaml.load(file, Loader=yaml.FullLoader)
      for k,v in input.items():
        if k == "image":
          if "frontend" in input["image"].keys():
            if "tag" in input["image"]["frontend"].keys():
              imageTagFrontend = input["image"]["frontend"]["tag"]
      if imageTagFrontend == "":      
        imageTagFrontend = "latest-prod"
      entryFrontend = {"name" : imageNameFrontend, "newName" : user_dockerhub+"/"+repo_name_frontend_dockerhub, "newTag" : imageTagFrontend}

    elif (tier == "frontend"):
      imageTagBackend = ""
      entryFrontend = {"name" : imageNameFrontend, "newName" : user_dockerhub+"/"+repo_name_frontend_dockerhub, "newTag" : image_tag}
      with open("./file.yaml") as file:
        input = yaml.load(file, Loader=yaml.FullLoader)
      for k,v in input.items():
        if k == "image":
          if "backend" in input["image"].keys():
            if "tag" in input["image"]["backend"].keys():
              imageTagBackend = input["image"]["backend"]["tag"]
      if imageTagBackend == "":
        imageNameBackend = "latest-prod"
      entryBackend = {"name" : imageNameBackend, "newName" : user_dockerhub+"/"+repo_name_backend_dockerhub, "newTag" : imageTagBackend}

  if "images" not in kustomization.keys():
    kustomization["images"] = [entryBackend, entryFrontend]
    #aggiungo scrivendo, la key patch
    with open(kustomization_path, "w") as file:
        yaml.dump(kustomization, file)
  else:
    #faccio overwrite
    kustomization["images"].clear()
    
    kustomization["images"].append(entryBackend)
    kustomization["images"].append(entryFrontend)

    with open(kustomization_path, "w") as file:
        yaml.dump(kustomization, file)
      
if __name__ == '__main__':
    main()
