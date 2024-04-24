#!/usr/bin/python3

def main():
  """
  convert KLA Nanomaterials .NMD to .hdf5 file (conversion of all metadata)

  in_file:
    label: KLA Nanomaterials binary file (.NMD)
    vendor: KLA Nanomaterials
    software:
  out_file:
    label: custom HDF5 with k-series/data as well as instrument and converter groups
  """
  import struct, os, json, sys, hashlib, re
  import numpy  as np
  import xmltodict
  import h5py

  convURI = b'https://github.com/micromechanics/tools/blob/main/nmd2hdf.py'
  convVersion = b'2.0'

  ## COMMON PART FOR ALL CONVERTERS
  fileNameIn = sys.argv[1]
  fileNameOut= os.path.splitext(fileNameIn)[0]+'.hdf5'
  fIn = open(fileNameIn,'rb')
  fOut  = h5py.File(fileNameOut, 'w')
  fOut.attrs['uri'] =     convURI
  fOut.attrs['version'] = convVersion
  fOut.attrs['original_file_name'] = fileNameIn
  md5Hash = hashlib.md5()
  md5Hash.update(fIn.read())
  fOut.attrs['original_md5sum'] = md5Hash.hexdigest()

  metaStartString = '<SAMPLE '
  metaEndString   = '</SAMPLE>'

  #get metadata from file-head
  fIn.seek(0)
  fileLength = os.path.getsize(fileNameIn)
  data = fIn.read()
  metaStart = data.hex().find(bytes(metaStartString,'latin-1').hex())
  metaStart = int(metaStart/2-1)  #divide by 2 because byte has 2 chars, subtract because first byte was cutoff
  metaEnd = data.hex().find(bytes(metaEndString,'latin-1').hex())
  metaEnd = int(metaEnd/2-1)
  fIn.seek(metaStart+1)
  data = fIn.read(metaEnd-metaStart+len(metaEndString))
  data = bytearray(source=data).decode('latin-1')
  # with open(os.path.splitext(fileNameIn)[0]+'.xml','w') as fTemp:
  #   fTemp.write(data)
  data = xmltodict.parse(data)
  dataString = json.dumps(data)
  fOut.attrs['default'] = b'test_1'
  instrument = fOut.create_group("instrument")
  instrument.attrs['json'] = dataString
  instrument.attrs['NX_class'] = b'NXinstrument'
  analysis = fOut.create_group("post_test_analysis")
  analysis.attrs['NX_class'] = b'NXparameters'
  software = analysis.create_group('com_github_micromechanics')


  #body of file: get data
  try:
    if isinstance(data['SAMPLE']['TEST'], list):
      numTest = len(data['SAMPLE']['TEST'])
    else:
      numTest = 1
    for iTest in range(numTest):
      hdfBranch_ = fOut.create_group('test_'+str(iTest+1))
      hdfBranch_.attrs['NX_class'] = b'NXentry'
      hdfBranch = hdfBranch_.create_group('data')
      hdfBranch.attrs['NX_class'] = b'NXdata'
      channelNames = []
      #first system channels
      if numTest==1:
        numSysChannel = len(data['SAMPLE']['TEST']['SYSCHANNEL'])
      else:
        numSysChannel = len(data['SAMPLE']['TEST'][iTest]['SYSCHANNEL'])
      for iChannel in range(numSysChannel):
        if numTest==1:
          name = data['SAMPLE']['TEST']['SYSCHANNEL'][iChannel]['@NAME']
        else:
          name = data['SAMPLE']['TEST'][iTest]['SYSCHANNEL'][iChannel]['@NAME']
        n = struct.unpack('i', fIn.read(4))[0]
        ddata = struct.unpack(str(n)+'d', fIn.read(8*n))
        dset = hdfBranch.create_dataset(re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower(), data=ddata)
        channelNames.append(re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower())
      #then calculated channels
      if numTest==1:
        numChannel    = len(data['SAMPLE']['TEST']['CHANNEL'])
      else:
        numChannel    = len(data['SAMPLE']['TEST'][iTest]['CHANNEL'])
      for iChannel in range(numChannel):
        if numTest==1:
          name = data['SAMPLE']['TEST']['CHANNEL'][iChannel]['@NAME']
        else:
          name = data['SAMPLE']['TEST'][iTest]['CHANNEL'][iChannel]['@NAME']
        n = struct.unpack('i', fIn.read(4))[0]
        ddata = struct.unpack(str(n)+'d', fIn.read(8*n))
        name = name.lower() if name in ['HARDNESS','MODULUS'] else re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        dset = hdfBranch.create_dataset(name, data=ddata)
        channelNames.append(name)
      if len([i for i in channelNames if 'load' in i])>0:
        hdfBranch.attrs['signal'] = [i for i in channelNames if 'load' in i][0]
      elif len([i for i in channelNames if 'force' in i])>0:
        hdfBranch.attrs['signal'] = [i for i in channelNames if 'force' in i][0]
      elif len([i for i in channelNames if 'time' in i])>0:
        hdfBranch.attrs['signal'] = [i for i in channelNames if 'time' in i][0]



    #test end
    if fIn.tell()==fileLength:
      print('Conversion successful')
    else:
      print("End not reached")
    fIn.close()
    fOut.close()
  except:
    fOut.close()
    os.unlink(fileNameOut)
    print('**ERROR in conversion')


if __name__ == "__main__":
  main()
