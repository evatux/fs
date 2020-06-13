from aux_types import ExtendableType
from spec import FATTR, DIR_ENTRY, DIR_ENTRY_SIZE, DIR_TYPE_MARK

RECTYPE = ExtendableType()
RECTYPE.EMPTY, RECTYPE.UNUSED, RECTYPE.DIR, RECTYPE.FILE = range(4)

class DirRecord:
    """
    Attributes
    ----------
    entry_first, entry_last : int

    Methods
    -------
    is_empty(), is_unused(), is_file(), is_dir() : bool
    name(), longname() : str
    cluster() : int
    entry_size() : int [static]
    """

    @staticmethod
    def entry_size():
        return DIR_ENTRY_SIZE

    def __init__(self, reader, entry_first):
        self.base_reader = reader
        self.entry_first = entry_first
        self.entry_last = self.entry_first + 1

        self.type = -1 # undef

        dir_type = self.reader().intr(offset=0, size=1)
        if dir_type == DIR_TYPE_MARK.EMPTY:
            self.type = RECTYPE.EMPTY
        elif dir_type == DIR_TYPE_MARK.UNUSED:
            self.type = RECTYPE.UNUSED
        if not self: return

        self.attr = self.reader().intr(DIR_ENTRY.ATTR)
        self.parse_longname_and_update_attr()

        if self.attr & FATTR.DIRECTORY:
            self.type = RECTYPE.DIR
        else:
            self.type = RECTYPE.FILE

        self._name = self.reader().read_bytes(DIR_ENTRY.NAME).decode("utf-8").rstrip(' ')
        self._ext = self.reader().read_bytes(DIR_ENTRY.EXT).decode("utf-8").rstrip(' ')
        self._cluster_high = self.reader().intr(DIR_ENTRY.CLUS_HIGH)
        self._cluster_low = self.reader().intr(DIR_ENTRY.CLUS_LOW)
        self._size = self.reader().intr(DIR_ENTRY.SIZE)

    def reader(self, entry_offset = -1):
        current_length = self.entry_last - self.entry_first
        pos = self.entry_first + (current_length + entry_offset) % current_length
        return self.base_reader.subreader(pos * DIR_ENTRY_SIZE)

    def __bool__(self):
        return not (self.is_empty() or self.is_unused())

    def __str__(self):
        if self.type == RECTYPE.EMPTY:
            return "<empty>"
        elif self.type == RECTYPE.UNUSED:
            return "<unused>"
        elif self.type == RECTYPE.DIR:
            return "[" + self.name(True) + "]"
        else:
            return self.name(True)

    def debug_str(self):
        return str(self.info())

    def info(self):
        d = {}

        d["entries"] = (self.entry_first, self.entry_last)
        d["type"] = ["empty", "unused", "dir", "file"][self.type]
        if not self: return d

        d["name"] = self.name()
        d["longname"] = self.longname()
        d["size"] = self.size()

        return d

    def is_empty(self):
        return self.type == RECTYPE.EMPTY

    def is_unused(self):
        return self.type == RECTYPE.UNUSED

    def is_file(self):
        return self.type == RECTYPE.FILE

    def is_dir(self):
        return self.type == RECTYPE.DIR

    def name(self, nice = False):
        if nice == True and self._longname:
            return self._longname
        if self._ext:
            return self._name + '.' + self._ext
        return self._name

    def longname(self):
        return self._longname

    def size(self):
        return self._size

    def cluster(self):
        return (self._cluster_high << 16) | self._cluster_low

    # private section

    def parse_longname_and_update_attr(self):
        if self.attr != FATTR.LFN:
            self._longname = None
            return

        self._longname = ""
        while self.attr == FATTR.LFN:
            raw = b''
            for offset, size in ((0x01, 10), (0x0E, 12), (0x1C, 4)):
                stop = False
                for i in range(size // 2):
                    ucs2 = b''
                    ucs2 += self.reader().read_bytes(offset = offset + 2 * i + 1)
                    ucs2 += self.reader().read_bytes(offset = offset + 2 * i + 0)
                    if ucs2 == b'\x00\x00':
                        stop = True
                        break
                    if not stop: raw += ucs2
                if stop: break

            self._longname = raw.decode("utf-16-be") + self._longname

            self.entry_last += 1
            self.attr = self.reader().intr(DIR_ENTRY.ATTR)
