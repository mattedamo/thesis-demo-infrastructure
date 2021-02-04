import os, yaml, sys

def main():
    args = sys.argv
    k = args[-1]
    with open("./config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    if k in ["app-name", "argocd-repo"]:
        if k not in config.keys():
            sys.exit(k + " not present in config file, add it")
        else:
            print(config[k])
    elif k == "prod-input-master":
        if k not in config.keys():
            print("backend")
        else:
            if config[k] not in ["backend", "frontend"]:
                sys.exit(k + " has not a valid value, it can be \"backend\" or \"frontend\" ")
            else:
                print(config[k])
        
if __name__ == "__main__":
    main()
