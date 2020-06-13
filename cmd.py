import sys

import fat32

class bcolors:
    RED   = "\033[1;31m"
    BLUE  = "\033[1;34m"
    CYAN  = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD    = "\033[;1m"
    REVERSE = "\033[;7m"

def cprint(color, *args, **kwargs):
    print(color, *args, **kwargs, end='')
    print(bcolors.RESET)

def error(*args, **kwargs):
    return cprint(bcolors.RED, '# error: ', *args, **kwargs)


fdisk = sys.argv[1] if len(sys.argv) >= 2 else "../fat32.disk"

def str_size(size):
    mod = ["B", "KB", "MB", "GB"]
    for i in range(len(mod)):
        if size < 10 * 1024: return "%5d %s" % (size, mod[i])
        size /= 1024

def print_ls(info_list):
    printable = [x for x in info_list if x["type"] in ("dir", "file")]
    printable.sort(key = lambda x: (x["type"], x["name"]))

    name = lambda x: x["longname"] if x["longname"] else x["name"]

    for x in printable:
        print("%s " % str_size(x["size"]), end='')
        if x["type"] == "dir":
            cprint(bcolors.BLUE, "[" + name(x) + "]")
        else:
            cprint(bcolors.GREEN, name(x))

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
                error("not such directory")
            else:
                walker = child_walker
        elif cmd.startswith('cat '):
            fname = cmd[4:]
            child_walker, size = fs.open(walker, fname)
            if not child_walker:
                error("not such file")
            else:
                print(fs.read_walker(child_walker, size).decode("ascii"), end='')
        elif cmd == "info.meta":
            print(fs.meta)
        else:
            error("unknown command. Known: cd, ls, exit")
