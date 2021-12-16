from github import Github
from github.GithubException import GithubException, UnknownObjectException
import os

def main():
    token = os.getenv('PAT_TOKEN',None)
    if not token:
        logging.error('PAT_TOKEN does not set')
        sys.exit(1)

    try:
        client = Github(token)
    except Exception as e:
        raise e

    repo_names = ["GeunjeLEE/dummy_plugin"]
    for repo_name in repo_names:
        repo = client.get_repo(repo_name)

        delete_all_workflows(repo)

        workflows = get_workflows('common')
        create_new_file_in_repository(repo, workflows)

def delete_all_workflows(repo):
    try:
        contents = repo.get_contents(".github/workflows",ref="master")
        for content in contents:
            message = f'CI: remove workflows ({content.path})'
            repo.delete_file(path=content.path, message=message, sha=content.sha, branch="master")
    except UnknownObjectException as e:
        print(e)

def get_workflows(group):
    workflow_path = f'./{group}/workflows'
    workflow_names = os.listdir(workflow_path)
    ignore = ['.gitkeep']

    ret = []
    for workflow_name in workflow_names:
        if workflow_name in ignore:
            continue
        workflow_info = {}
        with open(f'{workflow_path}/{workflow_name}','r') as f:
            body = f.read()
        path = f'.github/workflows/{workflow_name}'
        workflow_info[path] = body
        ret.append(workflow_info)

    return ret

def create_new_file_in_repository(repo, workflows):
    try:
        for workflow in workflows:
            for path,content in workflow.items():
                message = f'CI: Deploy CI ({path})'
                ret = repo.create_file(path=path, message=message, content=content, branch="master")
                print(f'file has been created to {repo.full_name} : {ret}')
    except GithubException as e:
        print(f'failed to file creation : {e}')
    except Exception as e:
        raise e

if __name__ == "__main__":
    main()