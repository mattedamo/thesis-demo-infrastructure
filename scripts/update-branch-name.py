#If default-input-file is set to true, if the branch is a feature or release branch, I have to update
#the name inside input.file, since it has a default branch name("release" or "branch")
import yaml, os, shutil

def main():
    code_branch = os.environ["CODE_BRANCH"]
    
    if "releases" or "features" in code_branch:
        with open("./input.yaml") as file:
            input = yaml.load(file, Loader=yaml.FullLoader)
        
        input["branch"] = code_branch

        with open("./input.yaml", "w") as file:
            yaml.dump(input, file)


if __name__ == '__main__':
    main()
