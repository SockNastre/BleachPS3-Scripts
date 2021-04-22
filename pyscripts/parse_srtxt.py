# Made by SockNastre
# Parses .srtxt binary files into .txt files so data from the srtxt can be read easily, special characters (icons, etc) are represented as hex

import os, sys

def read_section(srtxt):
    parsedData = ""
    c = int.from_bytes(srtxt.read(4), 'big')

    while c != 0:
        if 31 < c < 127: # If it's in the normal range of ASCII chars
            parsedData += str(chr(c))
        else:
            parsedData += hex(c)
        
        c = int.from_bytes(srtxt.read(4), 'big')
    return parsedData

# Path of inputted file
path = sys.argv[1]
srtxt = open(path , 'rb')

# Header reading
sectionCount = int.from_bytes(srtxt.read(4), 'big')
sectionOffsetArray = []

for _ in range(sectionCount):
    sectionOffsetArray.append(int.from_bytes(srtxt.read(4), 'big'))

# Stores the parsed data to be written to a text file
parsedData = ""

# Reading section data
for offset in sectionOffsetArray:
    srtxt.seek(offset)
    parsedData += read_section(srtxt) + '\n'

# Splits extension from path
pre, ext = os.path.splitext(path)
outputPath = pre + ".txt"

# Outputs text file
with open(outputPath, 'w') as txt:
    txt.write(parsedData)
