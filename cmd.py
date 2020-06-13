import sys

import fat32

fdisk = sys.argv[1] if len(sys.argv) >= 2 else "../fat32.disk"

def print_ls(info_list):
    printable = [x for x in info_list if x["type"] in ("dir", "file")]
    sorted(printable, key = lambda x: (x["type"], x["name"]))

    name = lambda x: x["longname"] if x["longname"] else x["name"]

    for x in printable:
        if x["type"] == "dir":
            print("[%s]" % name(x))
        else:
            print("%s" % name(x))

if __name__ == "__main__":
    fs = fat32.Fat(fdisk)
    walker = fs.root_walker()

    while True:
        print("> ", end='', flush=True)
        cmd = sys.stdin.readline().strip()
        if cmd in ("exit", "quit"):
            print("bye")
            sys.exit(0)
        elif cmd == "ls":
            print_ls(fs.ls(walker))
        elif cmd.startswith('cd '):
            subdir = cmd[3:]
            if subdir == '/':
                walker = fs.root_walker()
                continue
            child_walker = fs.cd(walker, subdir)
            if not child_walker:
                print("# [error] not such directory")
            else:
                walker = child_walker
        elif cmd == "info.meta":
            print(fs.meta)
        else:
            print("# [error] unknown command. Known: cd, ls, exit")
