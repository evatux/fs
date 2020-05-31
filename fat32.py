from aux_types import ExtendableType, FileReader
from spec import BPB

import dir_entry

class Meta(ExtendableType):
    def __init__(self, raw):
        # BPB
        self.BytesPerSec = raw.intr(BPB.BYTES_PER_SEC)
        self.SecPerClus = raw.intr(BPB.SEC_PER_CLUS)
        self.ReservedSecCount = raw.intr(BPB.RESERVED_SEC_COUNT)
        self.NumFats = raw.intr(BPB.NUM_FATS)
        self.FatSize = raw.intr(BPB.FAT_SIZE)
        self.RootClus = raw.intr(BPB.ROOT_CLUS)
        self.Signature = raw.intr(BPB.SIGNATURE)

        # Derived Aux Fields
        self.FirstDataSector = self.ReservedSecCount + \
                self.NumFats * self.FatSize


class Fat:
    def __init__(self, raw_fs_filename):
        self.raw = FileReader(raw_fs_filename)
        self.meta = Meta(self.raw)

        self.RootClusterOffset = self.cluster_offset(self.meta.RootClus)
        self.CurrentSector = self.RootClusterOffset

    def cluster_offset(self, offset):
        return self.meta.FirstDataSector + (offset - 2) * self.meta.SecPerClus

    def ls(self):
        sector_reader = self.raw.subreader(self.CurrentSector * self.meta.BytesPerSec)

        next_entry = 0
        while True:
            record = dir_entry.DirRecord(sector_reader, next_entry)
            print("%s\n%s\n" % (record, record.debug_str()))

            if record.is_empty():
                break

            next_entry = record.entry_last


