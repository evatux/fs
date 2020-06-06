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
        self.TotalSec32 = raw.intr(BPB.TOTAL_SEC_32)
        self.FatSize = raw.intr(BPB.FAT_SIZE)
        self.RootClus = raw.intr(BPB.ROOT_CLUS)
        self.Signature = raw.intr(BPB.SIGNATURE)

        # Derived Aux Fields
        self.FirstDataSector = self.ReservedSecCount + \
                self.NumFats * self.FatSize
        self.DataSectors = self.TotalSec32 - self.FirstDataSector
        self.MaxClusters = self.DataSectors / self.SecPerClus + 1


class FatWalker:
    def __init__(self, raw_fs, meta, cluster_base):
        self.raw_fs = raw_fs
        self.meta = meta
        self.fat_reader = raw_fs.subreader(
                self.meta.ReservedSecCount * self.meta.BytesPerSec)

        self.cluster_base = cluster_base
        self.cluster_list = [self.cluster_base]
        self.pos = 0

    def step(n_clusters = 1):
        if self.pos + n_clusters < self.len():
            self.pos += n_clusters
            assert self.pos >= 0
            return

        n_clusters -= self.len() - 1 - self.pos

        for i in range(n_cluster):
            assert(self.cluster_list[-1] <= self.MaxCluster)
            next_cluster = self.next_cluster(self.cluster_list[-1])
            self.cluster_list.append(next_cluster)

        self.pos = self.len() - 1

    def len(self):
        return len(self.cluster_list)

    def cluster_reader(self):
        cluster = self.cluster_list[self.pos]
        assert self.__valid_cluster(cluster)
        return self.raw_fs.subreader(
                self.cluster_offset_in_sectors(cluster) * self.meta.BytesPerSec)

    # private methods

    def next_cluster(self, cluster):
        return self.fat_reader.intr(offset = cluster * 4, size = 4)

    def cluster_offset_in_sectors(self, offset):
        return self.meta.FirstDataSector + (offset - 2) * self.meta.SecPerClus

    def __valid_cluster(self, cluster):
        return 0 <= cluster and cluster <= self.meta.MaxClusters


class Fat:
    def __init__(self, raw_fs_filename):
        self.raw = FileReader(raw_fs_filename)
        self.meta = Meta(self.raw)

    def ls(self):
        walker = FatWalker(self.raw, self.meta, self.meta.RootClus)
        sector_reader = walker.cluster_reader()

        next_entry = 0
        while True:
            record = dir_entry.DirRecord(sector_reader, next_entry)
            print("%s\n%s\n" % (record, record.debug_str()))

            if record.is_empty():
                break

            next_entry = record.entry_last


