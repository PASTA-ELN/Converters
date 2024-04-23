#!/usr/bin/python3
"""
convert Doli .mvl to .hdf5 file (partial conversion of 15 metadata)

in_file:
  label: Doli binary file (.mvl) for tension-compression machine
  vendor: Doli (www.doli.de)
  software: Test&Motion (Software for Universal Test Machines for Windows) Version 4.1
out_file:
  label: custom HDF5 with k-series as well as metadata and converter groups
"""
import struct, sys, os, hashlib, re
import h5py                                    #CWL requirement
import numpy as np
from datetime import datetime

convURI = b'https://github.com/micromechanics/tools/blob/main/converter_mvl.py'
convVersion = b'2.0'

## COMMON PART FOR ALL CONVERTERS
fileNameIn = sys.argv[1]
fileNameOut= os.path.splitext(fileNameIn)[0]+'.hdf5'
fIn   = open(fileNameIn,'br')
fOut  = h5py.File(fileNameOut, 'w')
fOut.attrs['uri'] =     convURI
fOut.attrs['version'] = convVersion
fOut.attrs['original_file_name'] = fileNameIn
md5Hash = hashlib.md5()
md5Hash.update(fIn.read())
fOut.attrs['original_md5sum'] = md5Hash.hexdigest()
fOut.attrs['default'] = b'test_1'
instrument = fOut.create_group("instrument")
instrument.attrs['NX_class'] = b'NXinstrument'
analysis = fOut.create_group("post_test_analysis")
analysis.attrs['NX_class'] = b'NXparameters'
software = analysis.create_group('com_github_micromechanics')

def addAttrs(offset, format, hdfBranch, key):
  # helper function: add attribute to branch
  if type(key)==list:
    fIn.seek(key[0])
    key = bytearray(source=fIn.read(key[1])).decode('latin-1')
    key = key.replace('\x00','').lower().replace(' ','_')   # ValueError: VLEN strings do not support embedded NULLs
    key = re.sub('[^a-z0-9_]','',key)
  fIn.seek(offset)
  if type(format)==int:
    value = bytearray(source=fIn.read(format)).decode('latin-1')
    if hdfBranch:
      hdfBranch.attrs[key] = value.replace('\x00','')
  else:
    value = struct.unpack(format, fIn.read(struct.calcsize(format)))
    if hdfBranch:
      if len(value)==0:
        hdfBranch.attrs[key] = value[0]
      else:
        hdfBranch.attrs[key] = value
  return value

def addData(format, hdfBranch, key, unit):
  # helper function: add data to branch
  data = fIn.read(struct.calcsize(format))
  if len(data) < struct.calcsize(format):
    return False
  data = struct.unpack(format, data)
  dset = hdfBranch.create_dataset(key, data=data)
  dset.attrs['unit'] = unit
  return True


try:
  ## SPECIFIC TO THIS CONVERTER: METADATA
  n    = addAttrs(0x2c,   'i',  None, '')[0]                  # size of datasets
  addAttrs(       0x2B50, 'i',  instrument, 'number_test')      # number of test
  date = addAttrs(0x2E3C, '6i', None, '')                     # date and time
  instrument.attrs['date'] = datetime(date[2],date[1],date[0],date[3],date[4],date[5]).isoformat()
  addAttrs(       0x529C,   64, instrument, 'name_method')      # name of method
  # 0x6A20-0x6BD8: unclear
  addAttrs(       0x7DE4,   36, instrument, 'name_folder')      # name of folder
  addAttrs(       0x7E09,   22, instrument, 'displacement_cell')# displacement cell
  addAttrs(       0x7E21,   22, instrument, 'load_cell')        # load cell
  for i in range(7):                                          # 7 key-value pairs
    addAttrs(0xA034+64*i,   64, instrument, [0xA674+32*i, 32])
  # 0x88A0: float : unclear
  addAttrs(       0xE29C,   36, instrument, 'file_prefix')      # file-prefix
  addAttrs(       0xE450,   64, instrument, 'path')             # path

  ## SPECIFIC TO THIS CONVERTER: DATA
  fIn.seek(0x10ea0)
  hdfBranch_ = fOut.create_group('test_1')
  hdfBranch_.attrs['NX_class'] = b'NXentry'
  hdfBranch = hdfBranch_.create_group('data')
  hdfBranch.attrs['NX_class'] = b'NXdata'
  hdfBranch.attrs['axes'] = b'displacement'
  hdfBranch.attrs['signal'] = b'force'

  addData(str(n)+'d', hdfBranch, 'time',         's')
  addData(str(n)+'f', hdfBranch, 'displacement', 'mm')
  addData(str(n)+'f', hdfBranch, 'force',        'N')
  # if more than 1 channels are stored:
  # - number of channels/sensors and its labeling are part of the machine configuration
  # - Machine configuration is stored in mdb database (MS standard jet) DB_UTM.mdb and there in table tblUTM
  #   -> use "mdb-export DB_UTM.mdb tblUTM > DB_UTM.csv" to convert it; Column "Machine1"
  # - this code: continue reading until failure
  idx = 0
  while True:
    idx += 1
    success = addData(str(n)+'f', hdfBranch, 'unlabeled_data_'+str(idx), '~')
    if not success:  #end of file
      break


  ## COMMON PART FOR ALL CONVERTERS
  fIn.close()
  fOut.close()
  print('Conversion successful')
except:
  fOut.close()
  os.unlink(fileNameOut)
  print('**ERROR in conversion')
