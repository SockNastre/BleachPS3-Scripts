# Made by SockNastre
# Turns .srtxt binary files into .txt files so text can be read, special characters (icons, etc) are represented as hex

import os, sys

# https://stackoverflow.com/a/18683105/10216412
def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]

# Path of inputted file
path = sys.argv[1]
srTxt = open(path , 'rb')

# Header reading
# https://stackoverflow.com/a/11713266/10216412
sectionCount = int.from_bytes(srTxt.read(4), byteorder='big')
sectionOffsets = []

# Stores the parsed data to be written to a txt
parsedData = ''

for _ in range(sectionCount):
    sectionOffsets.append(int.from_bytes(srTxt.read(4), byteorder='big'))

# Spits out info about the srtxt while reading section data
print("Section Count: " + str(sectionCount) + "\n\nData Offsets:")
for i in sectionOffsets:
    print(i)
    srTxt.seek(i)
    c = int.from_bytes(srTxt.read(4), byteorder='big')

    while c != 0:
        if (c >= 32 and c <= 126):
            # https://stackoverflow.com/a/3673447/10216412
            parsedData += str(chr(c))
        else:
	    # Special hex icons have '-' appended.
            parsedData += hex(c) + '-'
        
        c = int.from_bytes(srTxt.read(4), byteorder='big')
    
    parsedData += '\n'
print('\n')
parsedData = remove_last_line_from_string(parsedData)

# Splits extension from path
pre, ext = os.path.splitext(path)
outputPath = pre + ".txt"

if os.path.exists(outputPath):
    raise FileExistsError("File \"" + outputPath + "\" already exists.")

# Outputs text file
with open(outputPath, 'w') as txt:
    txt.write(parsedData)