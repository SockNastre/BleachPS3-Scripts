# Made by SockNastre
# Unpacks .spk archives

import os, sys

class Section:
    def __init__(self, offset, size, format):
        self.offset = offset
        self.size = size
        self.format = format

def calculate_size_with_padding(size, multiple, addMultiple = 1):
    while size % multiple != 0:
        size += addMultiple
    return size

def is_valid_texcol(spk, offset):
    spk.seek(offset)
    flags = int.from_bytes(spk.read(4), 'big')
    if (flags == 0x020101FF or flags == 0x01010001): # 0x020101FF is normal texture collection and 0x01010001 is layered texture collection
        return True
    return False

# TO-DO: Sometimes marks non-srtxt files as srtxt, needs improvement.
def is_valid_srtxt(spk, size, offset):
    spk.seek(offset)
    textSectionCount = int.from_bytes(spk.read(4), 'big')

    # TO-DO: Change this if-else statement to see if I can simplify it
    if (0 < textSectionCount <= size):
        sectionOffsetArray = [ 0, 4 ]
        for i in range(textSectionCount):
            offset = int.from_bytes(spk.read(4), 'big')
            
            for readSectionOffset in sectionOffsetArray:
                if offset == readSectionOffset:
                    return False
            
            if (offset % 4 != 0 or size <= offset):
                return False

            sectionOffsetArray.append(offset)
        return True
    else:
        return False

def is_valid_model(spk, offset):
    spk.seek(offset)
    if (int.from_bytes(spk.read(4), 'big') == 0x01105555):
        return True
    return False

def is_valid_seq(spk, offset):
    spk.seek(offset)
    if (int.from_bytes(spk.read(4), 'big') == 0x73657100): # "seq\x00"
        return True
    return False

# Path of inputted file
path = sys.argv[1]
spk = open(path , 'rb')

# Reading header
# Two offsets are read at once because the first offset is always 0
sectionOffsetArray = [ int.from_bytes(spk.read(4), 'big') ]
offset = int.from_bytes(spk.read(4), 'big')

# if offset is 0, we hit padding
# If offset is 1, we hit a section magic
while offset != 0 and offset != 1:
    sectionOffsetArray.append(offset)
    offset = int.from_bytes(spk.read(4), 'big')

# Need to subtract 4 from position because we read an extra (possibly invalid) integer
headerSize = calculate_size_with_padding(spk.tell() - 4, 16, 4)
sectionDataArray = []

for off in sectionOffsetArray:
    spk.seek(off + headerSize) # Offsets relative to end of header
    if (int.from_bytes(spk.read(4), 'big') != 1):
        exit("Offset: " + str(off + headerSize) + "\nError: Invalid section magic number.")
    
    spk.seek(16, 1) # Skips padding
    sectionDataSize = int.from_bytes(spk.read(4), 'big')
    sectionFormat = int.from_bytes(spk.read(4), 'big')
    spk.seek(4, 1) # Skips padding

    sectionDataArray.append(Section(spk.tell(), sectionDataSize, sectionFormat))

# Splits extension from path
pre, ext = os.path.splitext(path)

count = 0
for section in sectionDataArray:
    ext = ".unk"
    offset = section.offset
    if is_valid_texcol(spk, section.offset):
        ext = ".texcol"
    elif is_valid_srtxt(spk, section.size, section.offset):
        ext = ".srtxt"
    elif is_valid_model(spk, section.offset):
        ext = ".model"
    elif is_valid_seq(spk, section.offset):
        ext = ".seq"

    spk.seek(section.offset)
    outputPath = pre + '_' + str(count) + ext
    
    # Outputs section
    with open(outputPath, 'wb') as sec:
        sec.write(spk.read(section.size))
    
    count += 1
