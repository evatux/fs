class ExtendableType:
    pass


class SizeOffsetType:
    def __init__(self, size, offset, name=""):
        self.size = size
        self.offset = offset
        self.name = name

    def __str__(self):
        return self.name


class SizeOffsetTypeSet:
    def __init__(self, entries):
        assert(isinstance(entries, (list, tuple)))

        self.entries = {}
        for entry in entries:
            assert(isinstance(entry, (list, tuple)) and len(entry) == 3)
            self.entries[entry[0]] = SizeOffsetType(entry[1], entry[2], entry[0])

    def __getattr__(self, attr):
        return self.entries[attr]

    def read(self, fr, base = 0):
        print(self.name)
        return fr.intr(base + self.offset, self.size)

# Readers

def sanitize_offset_size(*args, **kwargs):
    if len(args) == 1:
        assert(isinstance(args[0], SizeOffsetType))
        return args[0].offset, args[0].size

    assert(len(args) == 0)
    return kwargs["offset"], kwargs.get("size", 1)


# General reader
class Reader:
    def __init__(self, reader, base_offset=0):
        self.reader = reader
        self.base_offset = base_offset

    def read_bytes(self, *args, **kwargs):
        offset, size = sanitize_offset_size(*args, **kwargs)
        kwargs["offset"] = self.base_offset + offset
        kwargs["size"] = size
        return self.reader.read_bytes(**kwargs)

    def intr(self, *args, **kwargs):
        offset, size = sanitize_offset_size(*args, **kwargs)
        kwargs["offset"] = self.base_offset + offset
        kwargs["size"] = size
        return self.reader.intr(**kwargs)

    def subreader(self, offset):
        return Reader(self, offset)


# File Reader
class FileReader:
    def __init__(self, filename):
        self.file = open(filename, "rb")

    def read_old(self, offset, size = 1):
        self.file.seek(offset, 0)
        for sz in range(size):
            b = self.file.read(1)
            i = int.from_bytes(b, "little", signed=False)
            print("[%8x : %8d] 0x%8X (%d)" % (offset + sz, offset + sz, i, i))

    def read_bytes(self, *args, **kwargs):
        offset, size = sanitize_offset_size(*args, **kwargs)

        self.file.seek(offset, 0)
        raw_bytes = self.file.read(size)
        if kwargs.get("debug", False):
            print("@@@ read_bytes [%8x : %8d] " % (offset, offset), b)
        return raw_bytes

    def intr(self, *args, **kwargs):
        offset, size = sanitize_offset_size(*args, **kwargs)
        raw_bytes = self.read_bytes(offset=offset, size=size)
        i = int.from_bytes(raw_bytes, "little", signed=False)
        if kwargs.get("debug", False):
            print("[%8x : %8d] 0x%X (%d)" % (offset, offset, i, i))
        return i

    def subreader(self, offset):
        return Reader(self, offset)
