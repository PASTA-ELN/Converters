# Converters
Converters from binary files to hdf5

Some people call it **Extractor**, **Translator**

The idea is to have a most literal translation without tranformation, i.e. from imperial units to SI

# List
- Doli - Test&Motion software

# Create a repository
## add your python file and example file
.
├── converter
│   └── converter_mvl.py
├── example_files
│   └── Membrane2_03.mvl
├── LICENSE
└── README.md
## Test and create requirements.txt
- Test current version
  python converter/converter_mvl.py example_files/Membrane2_03.mvl
- Create venv and activate
  python -m venv venv
  . ./venv/bin/activate
- Add venv to .gitignore
  cat > .gitignore
- Create requirements file, install it and test
  touch requirements.txt
  pip install -r requirements.txt
  python converter/converter_mvl.py example_files/Membrane2_03.mvl
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
└── requirements.txt
# Create my own fork on github in a totally separate folder
https://github.com/datatractor/yard
- fork that repository, click ok
- git clone that forked repository

- sudo apt install git-lfs
- cd yard/marda_registry/data/lfs/
- mkdir doli-mvl
- git lfs install (only necessary once)
- cd ..

in yard folder
 - git checkout -b steffen
 - git add marda_registry/data/lfs/doli-mvl/*
 - git lfs ls-files
 - git remote add origin2 git@github.com:SteffenBrinckmann/metadata_extractors_registry.git
 - git push --set-upstream origin2 steffen

change to "base repository"=datatractor/yard on Github during creation of PR

- Add to pyproject.toml in [project.scripts] section at end

