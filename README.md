# Converters
Converters from binary files to hdf5 / nexus format

Some people call it **Extractor**, **Translator**

The idea is to have a most literal translation without tranformation, i.e. from imperial units to SI

# List
- Doli - Test&Motion software
- Fischer Scope Indenter
- KLA G200X Nanoindenter


# What to do after the first submit
## Update this repository
- add to above list
- add converter to own repository and use a main function
- add example files to own repository
- add yml files for filetype
- append to extractor.yml file
- append to pyproject.toml file
## Update yadg
- copy extractor.py
- copy all filetype files
- copy all example files


# How to create this repository
## add your python file and example file
.
├── converter
│   └── converter_mvl.py
├── example_files
│   └── Membrane2_03.mvl
├── LICENSE
├── README.md
└── pyproject.toml

Copy pyproject.toml from here

## Test and create requirements.txt
- Test current version: converter should have a main function which is called
  "python converter/converter_mvl.py example_files/Membrane2_03.mvl"
- Create venv and activate
  "python -m venv venv"
  ". ./venv/bin/activate"
- Add venv to .gitignore
  "cat > .gitignore"
- Create requirements file, install it and test
  "touch requirements.txt"
  "pip install -r requirements.txt"
  "python converter/converter_mvl.py example_files/Membrane2_03.mvl"

## Final structure
- test in empty environment
.
├── converter
│   └── converter_mvl.py
├── example_files
│   ├── Membrane2_03.hdf5
│   └── Membrane2_03.mvl
├── LICENSE
├── README.md
├── pyproject.toml
└── requirements.txt

Append to pyproject.toml in [project.scripts] section at end
- to change to these type of extractor

# How to add these converters to the MARDA - YARD repository
## Create my own fork on github in a totally separate folder
- go to https://github.com/datatractor/yard
- fork that repository, click ok
- git clone that forked repository

Install git lfs
- "sudo apt install git-lfs"
- "cd yard/marda_registry/data/lfs/"
- "mkdir doli-mvl"
- "git lfs install" (only necessary once)

Copy from your repository to this forked repository
- extractor.yml
- filetype.yml
- example files

In main yard folder
 - "git checkout -b new_branch"
 - "git add marda_registry/data/lfs/doli-mvl/*"
 - "git lfs ls-files"
 - "git push --set-upstream origin new_branch"

Go to the shown link to create a pull-request
- change to "base repository"=datatractor/yard on Github during creation of PR
