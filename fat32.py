import aux_types
from spec import BPB

from spec import DIR_TYPE_MARK # TODO: remove
import dir_entry

class Meta(aux_types.ExtendableType):
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
        self.raw = aux_types.FileReader(raw_fs_filename)
        self.meta = Meta(self.raw)

        self.RootClusterOffset = self.cluster_offset(self.meta.RootClus)
        self.CurrentSector = self.RootClusterOffset

    def cluster_offset(self, offset):
        return self.meta.FirstDataSector + (offset - 2) * self.meta.SecPerClus

    def ls(self):
        i = 0
        while True:
            entry = dir_entry.DirEntry(self.raw.subreader(self.CurrentSector * self.meta.BytesPerSec), i)
            i = i + 1
            if entry.type == DIR_TYPE_MARK.EMPTY:
                break
            else:
                print(entry.filename)


