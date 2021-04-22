# Made by SockNastre
# Extracts textures from .texcol

import os, sys
import struct

class TextureRecord:
    def __init__(self, index, offset, dataSize, fourCCFlag, mipmapCount, width, height):
        self.index = index
        self.offset = offset
        self.dataSize = dataSize
        self.fourCCFlag = fourCCFlag
        self.mipmapCount = mipmapCount
        self.width = width
        self.height = height

def get_fourcc(flag):
    return{
        0x86 : b"DXT1",
        0x88 : b"DXT5",
    }.get(flag, b"UNK" + struct.pack('I', flag))

# Path of inputted file
path = sys.argv[1]
texcol = open(path , 'rb')

# Header reading
flags = int.from_bytes(texcol.read(4), 'big')

if flags == 0x020101FF: # Normal texture collection
    textureDataSize = int.from_bytes(texcol.read(4), 'big')
    textureCount = int.from_bytes(texcol.read(4), 'big')
    textureRecordArray = []

    # Loops through texture records
    for _ in range(textureCount):
        index = int.from_bytes(texcol.read(4), 'big')
        offset = int.from_bytes(texcol.read(4), 'big')
        dataSize = int.from_bytes(texcol.read(4), 'big')
        fourCCFlag = int.from_bytes(texcol.read(1), 'big')
        mipmapCount = int.from_bytes(texcol.read(1), 'big')
        texcol.seek(6, 1) # Skips unk meta 1
        width = int.from_bytes(texcol.read(2), 'big')
        height = int.from_bytes(texcol.read(2), 'big')
        texcol.seek(12, 1) # Skips unk meta 2

        textureRecordArray.append(TextureRecord(index, offset, dataSize, fourCCFlag, mipmapCount, width, height))
    
    # Splits extension from path
    pre, spkExt = os.path.splitext(path)

    for texture in textureRecordArray:
        outputPath = pre + '_' + str(texture.index) + ".dds"
        with open(outputPath, 'wb') as dds:
            dds.write(b"DDS ") # Magic
            dds.write(struct.pack('I', 0x7C)) # Header size
            dds.write(struct.pack('I', 0x0A100700)) # Flags
            dds.write(struct.pack('I', texture.width))
            dds.write(struct.pack('I', texture.height))
            
            dds.write(bytearray(8))
            dds.write(struct.pack('I', texture.mipmapCount))
            dds.write(bytearray(44))

            dds.write(struct.pack('I', 32))
            dds.write(struct.pack('I', 4))

            fourCC = bytearray()
            fourCC.extend(get_fourcc(texture.fourCCFlag))
            dds.write(fourCC)
            
            # Not finished yet
