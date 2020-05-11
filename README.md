:warning: :warning: :warning: :warning: :warning: 

**_This repository is deprecated._**

**_The new public GitHub repository for AOS-CX python modules is [here](https://github.com/aruba/pyaoscx)._**

**_To install the official pyaoscx modules, please follow the instructions located on the readthedocs page [here](https://pyaoscx.readthedocs.io/en/latest/)._**  

:warning: :warning: :warning: :warning: :warning: 

---

# aos-cx-python

These scripts are written for AOS-CX API v1 and v10.04. These scripts are written for devices running AOS-CX firmware version 10.04.

For this initial release, it is recommended to use the v1 AOS-CX API.  See the Release Notes for more information.

## Structure

* REST API call functions are found in the files in /src.
* REST API call functions are combined into other functions that emulate low-level processes. These low-level process functions are also placed in files in /src.
* Functions from the /src files (API functions and low-level functions) are combined to emulate larger network configuration processes (workflows). These workflow scripts stored in the /workflows folder.
* Data to be imported into functions is stored in the /sampledata folder.

## How to contribute

Please see the accompanying CONTRIBUTING.md file for guidelines on how to contribute to this repository.

## Git Workflow

This repo adheres to the 'shared repo' git workflow:
1. Clone the repo to a local machine:

    ```git clone <repo_URL>```
2. Checkout a local working branch:

    ```git checkout -b <local_working_branch_name>```
3. Add and amend files in the local working branch:

    ```git add <file_name>```
4. Commit regularly. Each commit should encompass a single logical change to the repo (e.g. adding a new function in /src is one commit; writing docstrings for all functions in a module is another commit). Include an explanatory message with each commit:

    ```git commit -m "<Clear_explanation_of_commit_here>"```
5. Push commits to github.hpe.com:

    ```git push origin <local_working_branch_name```
6. Merge changes using a Pull Request on github.hpe.com. Ensure the PR has a relevant title and additional comments if necessary. PRs should be raised regularly once code is tested and the user satisfied that it is ready for submission. Do not put off creaing a PR until a whole project is complete. The larger the PR, the difficult it is to successfully merge.

## Setup
Before starting ensure the switch REST API is enabled. Instructions for checking and changing whether or not the REST API is enabled status are available in the *ArubaOS-CX Rest API Guide*. 
This includes making sure each device has an administrator account with a password, and each device has https-server rest access-mode read-write and enabled on the reachable vrf.

### How to run this code
In order to run the workflow scripts, please complete the steps below:
1. install virtual env (refer https://docs.python.org/3/library/venv.html). Make sure python version 3 is installed in system.
    
    ```
    $ python3 -m venv switchenv
    ```
2. Activate the virtual env
    ```
    $ source switchenv/bin/activate
    in Windows:
    $ venv/Scripts/activate.bat
    ```
3. Install all packages required from requirements file
    ```
    (switchenv)$ pip install -r <path>/<to>/aos-cx-python/requirements.txt
    ```
4. Go to `aos-cx-python/sampledata/` YAML file that corresponds to the workflow that you want to run and fill out the information appropriate to the environment and topology.  It is recommended that these scripts can reach each individual device through dedicated Out-Of-Band Management access to prevent any disconnects through the workflows.  
5. Now you can run different workflows from aos-cx-python/workflows (e.g. `print_system_info.py`) 
6. Keep in mind that the workflows perform high-level configuration processes; they are highly dependent on the configuration already on the switch prior to running the workflows. For this reason, the comment at the top of each workflow script describes any necessary preconditions.

## Troubleshooting Issues
1. If you encounter module import errors, make sure that the path to the repo's top-level directory (i.e. `<path>/<to>/aos-cx-python`) is in the PYTHONPATH.
2. When you execute a workflow script, if you don't specify the login credentials in the YAML data file, then you will be prompted to enter the username and password. PyCharm has a bug where you won't be able to enter the credentials if you execute the script normally via Run (play button). It will work however if you execute the script via Debug (bug button).

Additionally, please read the RELEASE-NOTES.md file for the current release information and known issues.
