from spec import FATTR, DIR_ENTRY, DIR_ENTRY_SIZE, DIR_TYPE_MARK


class DirEntry:
    def __init__(self, reader, index):
        self.reader = reader.subreader(DIR_ENTRY_SIZE * index)
        self.type = self.reader.intr(offset=0, size=1)

        if self.type in (DIR_TYPE_MARK.EMPTY, DIR_TYPE_MARK.UNUSED):
            return

        self.attr = self.reader.intr(DIR_ENTRY.ATTR)
        if self.attr == FATTR.LFN:
            self.filename = self.get_longname()
        else:
            self.filename = self.get_name()

    def get_name(self):
        return self.reader.read_bytes(DIR_ENTRY.NAME).decode("utf-8")

    def get_longname(self):
        return "long_name"

