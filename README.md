# Converters
Converters from binary files to hdf5 / nexus format

Some people call it **Extractor**, **Translator**

The idea is to have a most literal translation without tranformation, i.e. from imperial units to SI

# List
- Doli - Test&Motion software
- Fischer Scope Indenter
- KLA G200X Nanoindenter

# Links
This repo was created to participate in the datatractor
https://github.com/datatractor/yard which shows the converters on
https://yard.datatractor.org/ while also having an API endpoint.

# How to add another converters
## Update this repository
- add to above list in Readme file
- add converter to this repository and ensure that a main function exists
- add example files to this repository
- add yml file for filetype
- append to extractor.yml file (all extractors of one repo are in one file)
- append extractor command to pyproject.toml file in [project.scripts] section at end

## Update your yadg fork
- copy extractor.py
- copy all filetype files
- copy all example files
- create a pull request

# How and why I created this repository
Datatractor requires that the extractor is installable, for instance via pip. This way a virtual environment can
be created and everything run there. Pip allows the specification of a repository "pip install git+https:\\github..."
without need for a pypi package. This repository just needs things to create a package: pyproject.toml

## Create file structure
.
├── converter
│   └── converter_mvl.py
├── example_files
│   └── Membrane2_03.mvl
├── marda_yml
│   ├── extractors
│   │   └── pasta-converters.yml
│   └── filetypes
│       └── doli-mvl.yml
├── LICENSE
├── README.md
├── .gitignore       (exclude all files you don't need)
├── pyproject.toml   (can copy from here and adopt)
└── requirements.txt

## Test and create requirements.txt
Create venv and activate

  "python -m venv venv"
  ". ./venv/bin/activate"
  "pip install -r requirements.txt"
  "python converter/converter_mvl.py example_files/Membrane2_03.mvl"

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
