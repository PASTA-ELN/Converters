#!/usr/bin/python3

def main():
  """
  convert Fischer Scope .hap to .hdf5 file (partial conversion of 15 metadata)

  in_file:
    label: Fischer Scope binary file (.hap) Nanoindenters
    vendor: Helmut Fischer GmbH+Co
    software: WIN-HCU
  out_file:
    label: custom HDF5 with k-series as well as metadata and converter groups
  """
  import struct, sys, os, hashlib
  import h5py                                    #CWL requirement
  import numpy as np
  from datetime import datetime

  convURI = b'https://github.com/micromechanics/tools/blob/main/hap2hdf.py'
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
    """
    helper function: add attribute to branch

    Args:
      offset: file offset
      format: data to read, int=numb. of chars, otherwise 4i
      hdfBrach: branch to add
      key: name of the key

    Returns:
      none
    """
    if type(key)==list:
      fIn.seek(key[0])
      key = bytearray(source=fIn.read(key[1])).decode('latin-1')
      key = key.replace('\x00','')   # ValueError: VLEN strings do not support embedded NULLs
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
    addAttrs(       0x171, 'd',  instrument, 'max_load')
    addAttrs(       0x179, 'd',  instrument, 'one_in_double')
    addAttrs(       0x181, 'd',  instrument, 'time_to_load')
    fIn.seek(0x189)
    data = struct.unpack('4i', fIn.read(struct.calcsize('4i')))
    # print('Unknown data of int',data)
    data = struct.unpack('3d', fIn.read(struct.calcsize('3d')))
    # print('Unknown data of double',data)
    data = struct.unpack('i', fIn.read(struct.calcsize('i')))
    # print('Unknown data of int',data)
    #data = struct.unpack('6d', fIn.read(struct.calcsize('6d')))
    ##....
    addAttrs(       0x55c,   40, instrument, 'name_folder')      # name of folder

    fIn.seek(0x4CF)
    locations = bytearray(source=fIn.read(10)).decode('latin-1')
    if locations == 'CKoordLine':
      nLocation = 0x5BD
    elif locations == 'CKoordArra':
      nLocation = 0x5C2
    else:
      nLocation = 0x52B
    n = addAttrs(nLocation, 'i',  instrument, 'number_test')[0] # number of test
    # "CKoordLine" contains start and end coordinates of line but not the individual points, and apparently also not the delta


    ## SPECIFIC TO THIS CONVERTER: DATA
    for iTest in range(n):
      pos=fIn.tell()
      # print('pos |',iTest,hex(pos))
      hdfBranch_ = fOut.create_group('test_'+str(iTest+1))
      hdfBranch_.attrs['NX_class'] = b'NXentry'
      hdfBranch = hdfBranch_.create_group('data')
      hdfBranch.attrs['NX_class'] = b'NXdata'
      hdfBranch.attrs['axes'] = b'displacement'
      hdfBranch.attrs['signal'] = b'force'
      content = fIn.read()
      marker = b'\xE8\x3F\x00\x00\x00\x00\x00\xC0\x57\x40\x00\x00\x00\x00\x00\x40\x50\x40\x00\x00\x00\x00\x00\x00\x59\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01'
      startData = content.find(marker)+len(marker)+pos+40

      fIn.seek(startData)
      nData = struct.unpack('h', fIn.read(struct.calcsize('h')))[0]
      addData(str(nData)+'d', hdfBranch, 'force', 'mN')
      nData2 = struct.unpack('h', fIn.read(struct.calcsize('h')))[0]  #same nData as before
      addData(str(nData)+'d', hdfBranch, 'displacement', 'um')
      endDisplacement = fIn.tell()

      searchString = "534D4330313700"
      data = fIn.read()
      found = data.hex().upper().find(searchString)
      found = int(found/2-1)+endDisplacement+129
      print("Time offset",found)
      fIn.seek(found)

      addData(str(nData)+'d', hdfBranch, 'time',        's')
      _ = struct.unpack('2i', fIn.read(struct.calcsize('2i')))

    ## COMMON PART FOR ALL CONVERTERS
    fIn.close()
    fOut.close()
    print('Conversion successful')
  except:
    fOut.close()
    os.unlink(fileNameOut)
    print('**ERROR in conversion')


if __name__ == "__main__":
  main()