import aux_types

# BPB - BIOS Parameter Block
BPB = aux_types.SizeOffsetTypeSet((
        ("BYTES_PER_SEC"      , 2, 0x0B),
        ("SEC_PER_CLUS"       , 1, 0x0D),
        ("RESERVED_SEC_COUNT" , 2, 0x0E),
        ("NUM_FATS"           , 1, 0x10),
        ("FAT_SIZE"           , 4, 0x24),
        ("ROOT_CLUS"          , 4, 0x2C),
        ("SIGNATURE"          , 2, 0x1FE),
        ))


# Directory entry
DIR_ENTRY_SIZE = 32
DIR_ENTRY = aux_types.SizeOffsetTypeSet((
        ("NAME"     , 8, 0x00),
        ("EXT"      , 3, 0x08),
        ("ATTR"     , 1, 0x0B),
        ("CLUS_HIGH", 2, 0x14),
        ("TIME"     , 2, 0x16),
        ("DATE"     , 2, 0x18),
        ("CLUS_LOW" , 2, 0x1a),
        ("SIZE"     , 4, 0x1c),
        ))


# Enrty attribute
FATTR = aux_types.ExtendableType()
FATTR.READONLY = 0x01
FATTR.HIDDEN = 0x02
FATTR.SYSTEM = 0x04
FATTR.VOLUMEID = 0x08
FATTR.DIRECTORY = 0x10
FATTR.ARCHIVE = 0x20
FATTR.LFN = FATTR.READONLY | FATTR.HIDDEN | FATTR.SYSTEM | FATTR.VOLUMEID


# Directory type
DIR_TYPE_MARK = aux_types.ExtendableType()
DIR_TYPE_MARK.EMPTY  = 0x00
DIR_TYPE_MARK.UNUSED = 0xE5
