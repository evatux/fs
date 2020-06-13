from aux_types import ExtendableType, FileReader
from spec import BPB

from dir_record import DirRecord

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
        self.ClusterSize = self.SecPerClus * self.BytesPerSec

    def __str__(self):
        ret = ">>> META.INFO <<<"
        ret += "\nBytesPerSec: " + str(self.BytesPerSec)
        ret += "\nSecPerClus: " + str(self.SecPerClus)
        ret += "\nReservedSecCount: " + str(self.ReservedSecCount)
        ret += "\nNumFats: " + str(self.NumFats)
        ret += "\nTotalSec32: " + str(self.TotalSec32)
        ret += "\nFatSize: " + str(self.FatSize)
        ret += "\nRootClus: " + str(self.RootClus)
        ret += "\nSignature: " + str(self.Signature)
        ret += "\nFirstDataSector: " + str(self.FirstDataSector)
        ret += "\nDataSectors: " + str(self.DataSectors)
        ret += "\nMaxClusters: " + str(self.MaxClusters)
        ret += "\nClusterSize: " + str(self.ClusterSize)
        ret += "\n>>>>>>>>.<<<<<<<<"
        return ret


class Walker:
    def __init__(self, raw_fs, meta, cluster_base):
        self.raw_fs = raw_fs
        self.meta = meta
        self.fat_reader = raw_fs.subreader(
                self.meta.ReservedSecCount * self.meta.BytesPerSec)

        self.cluster_list = [cluster_base]
        self.pos = 0

    def step(self, n_clusters = 1):
        if self.pos + n_clusters < self.len():
            self.pos += n_clusters
            assert self.pos >= 0
            return

        n_clusters -= self.len() - 1 - self.pos

        for _ in range(n_clusters):
            assert(self.__valid_cluster(self.cluster_list[-1]))
            next_cluster = self.next_cluster(self.cluster_list[-1])
            print("@@@ next_cluster: ", next_cluster)
            self.cluster_list.append(next_cluster)

        self.pos = self.len() - 1

    def len(self):
        return len(self.cluster_list)

    def is_last(self):
        return self.cluster_list[self.pos] > self.meta.MaxClusters

    def cluster_reader(self):
        cluster = self.cluster_list[self.pos]
        assert self.__valid_cluster(cluster)
        return self.raw_fs.subreader(
                self.cluster_offset_in_sectors(cluster) * self.meta.BytesPerSec)

    # private methods

    def next_cluster(self, cluster):
        return self.fat_reader.intr(offset = cluster * 4, size = 4) & 0x0FFFFFFF

    def cluster_offset_in_sectors(self, offset):
        return self.meta.FirstDataSector + (offset - 2) * self.meta.SecPerClus

    def __valid_cluster(self, cluster):
        ok = 2 <= cluster and cluster <= self.meta.MaxClusters
        if not ok: print("@@@ assert: cluster = ", cluster)
        return ok


class Fat:
    def __init__(self, raw_fs_filename):
        self.raw = FileReader(raw_fs_filename)
        self.meta = Meta(self.raw)

    def root_walker(self):
        return Walker(self.raw, self.meta, self.meta.RootClus)

    def ls(self, walker):
        ret = []

        cluster_reader = walker.cluster_reader()

        next_entry = 0
        while True:
            record = DirRecord(cluster_reader, next_entry)

            # print("%s\n%s\n" % (record, record.debug_str()))
            ret.append(record.info())

            if record.is_empty(): return ret # end of directory

            next_entry = record.entry_last
            if next_entry * DirRecord.entry_size() == self.meta.ClusterSize:
                walker.step()
                if walker.is_last(): return ret # last cluster (could this happen ?)
                cluster_reader = walker.cluster_reader()
                next_entry = 0

    def cd(self, parent_walker, dir_name):
        cluster_reader = parent_walker.cluster_reader()

        next_entry = 0
        while True:
            record = DirRecord(cluster_reader, next_entry)

            if record.is_empty(): return None # end of directory

            if record.is_dir():
                match = dir_name.lower() == record.name().lower()
                if not match:
                    lname = record.longname()
                    if lname: match = dir_name.lower() == lname.lower()
                if match:
                    return Walker(self.raw, self.meta, record.cluster())

            next_entry = record.entry_last
            if next_entry * DirRecord.entry_size() == self.meta.ClusterSize:
                parent_walker.step()
                if parent_walker.is_last(): return # last cluster (could this happen ?)
                cluster_reader = parent_walker.cluster_reader()
                next_entry = 0

        return None
