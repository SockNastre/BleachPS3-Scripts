# Made by SockNastre
# Parses resFat*.bin binary files into .txt files so data from the resFat can be read easily

import os, sys

class SPK:
    def __init__(self, offset, sectionCount, misc):
        self.offset = offset
        self.sectionCount = sectionCount
        self.misc = misc
        self.sectionFormatArray = []
        self.strOffset = 0
        self.entryStr = ""

def get_section_format(formatNum):
    return{
        0 : "GeneralData",
        1 : "TextureData_A",    # ModelTextures?
        2 : "MeshData",         # ?
        5 : "TextureData_B",    # PairedTextures/MiscTextures?
        6 : "UnknownData",      # StageMeshes?
        7 : "TextureData_C"     # LayeredTextures/EffectTextures/MapTextures?
    }.get(formatNum, str(formatNum))

def read_null_terminated_str(file):
    stringResult = ""
    c = file.read(1)

    while c != b'\x00':
        stringResult += str(c, 'utf-8')
        c = file.read(1)
    return stringResult

# Path of inputted file
path = sys.argv[1]
resFat = open(path , 'rb')

# Reading header
if (int.from_bytes(resFat.read(4), 'big') != 1):
    exit("Error: Invalid magic number.")

spkRecordsOffset = int.from_bytes(resFat.read(4), 'big')
strRecordsOffset = int.from_bytes(resFat.read(4), 'big')
spkCount = int.from_bytes(resFat.read(4), 'big')
spkDataArray = []

# Goes to spk records, where size and offset of spk metadata is stored along ADD MORE HERE
resFat.seek(spkRecordsOffset)

for _ in range(spkCount):
    offset = int.from_bytes(resFat.read(4), 'big') # Later some math has to be done to get the true offset, look at line 48 for that
    sectionCount = int.from_bytes(resFat.read(4), 'big')
    misc = resFat.read(8)

    spk = SPK(offset + sectionCount * 16, sectionCount, misc)
    spkDataArray.append(spk)

for spk in spkDataArray:
    resFat.seek(spk.offset)

    for _ in range(spk.sectionCount):
        resFat.seek(24, 1) # Skips magic number and padding
        sectionFormat = int.from_bytes(resFat.read(4), 'big')
        spk.sectionFormatArray.append(sectionFormat)        
        resFat.seek(4, 1) # Skips padding

# Goes to where spk entry string records are stored, size and offset (relative to data section) of spk entry string
resFat.seek(strRecordsOffset)

if (int.from_bytes(resFat.read(4), 'big') != 24):
    exit("Error: Invalid string data section magic number.")

strRecordsSize = int.from_bytes(resFat.read(4), 'big')
strArrayOffset = strRecordsOffset + strRecordsSize

if (resFat.read(4) != b"data"):
    exit("Error: Invalid string data section magic number.")

strOffsetArray = []

# Skips padding
resFat.seek(12, 1)

for spk in spkDataArray:
    resFat.seek(4, 1) # Skips entry string array offset (relative to beginning of entry string data section)
    strOffset = int.from_bytes(resFat.read(4), 'big') # Relative to strArrayOffset

    spk.strOffset = strArrayOffset + strOffset

for spk in spkDataArray:
    resFat.seek(spk.strOffset)
    spk.entryStr = read_null_terminated_str(resFat)

# Stores the parsed data to be written to a text file
parsedData = ""

for spk in spkDataArray:
        parsedData += spk.entryStr +  ':'

        for i in range(spk.sectionCount):
            parsedData += "\n\t" + str(i) + " - " + get_section_format(spk.sectionFormatArray[i])

        parsedData += "\n\n"

# Splits extension from path
pre, ext = os.path.splitext(path)
outputPath = pre + ".txt"

# Outputs parsed resFat text file
with open(outputPath, 'w') as txt:
    txt.write(parsedData)
