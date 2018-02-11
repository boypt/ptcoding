import sys
import os

paths = [ "/mnt/sda1", "/mnt/xzb/TDDOWNLOAD" ]

def main():
    hashes = {}
    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                fsize = os.path.getsize(full_path)
                if fsize > 4096 and fsize in hashes:
                    print('#duplicate found {0}: \nrm -fv "{1}"\nrm -rf "{2}"\n'.format(fsize,full_path, hashes[fsize]))
                else:
                    hashes[fsize] = full_path

if __name__ == "__main__":
    main()

