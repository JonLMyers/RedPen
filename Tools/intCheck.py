#!/usr/bin/python
import sqlite3 as lite
import os
import sys
import hashlib
import getopt


STATUS_UNMODIFIED = 'Unmodified'
STATUS_MODIFIED = 'WARNING: FILE MODIFIED'
STATUS_NEW = 'New File'
FULL_FILES = []


def get_hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main(argv):
    try:
        con = lite.connect('integrity.db')
        cur = con.cursor()
    except lite.Error, e:
        print("Error {}").format(e.args[0])
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv, "hd:", ["directory="])
    except getopt.GetoptError:
        print("intCheck.py -d <DIRECTORY>")

    for opt, arg in opts:
        if opt == '-h':
            print('intCheck.py -d <DIRECTORY>')
            sys.exit()
        elif opt in ("-d"):
            directory = arg
        else:
            directory = "C:/"

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            #print(os.path.join(root, filename))
            FULL_FILES.append(os.path.join(root, filename))

    for filename in FULL_FILES:
        fhash = get_hash(filename)

        with con:
            con.row_factory = lite.Row
            cur = con.cursor()

            try:
                cur.execute("SELECT * FROM Files WHERE Filename=?", (filename,))
            except lite.Error, e:
                cur.execute("CREATE TABLE Files(Filename TEXT, Hash TEXT, Status TEXT)")
                cur.execute("SELECT * FROM Files WHERE Filename=?", (filename,))

            row = cur.fetchone()

            if row:
                if row[1] == fhash:
                    print("File {}: {}").format(filename, STATUS_UNMODIFIED)
                    cur.execute("UPDATE Files set Status=? WHERE Hash=?",
                                (STATUS_UNMODIFIED, fhash,))
                else:
                    print("File {}: {}").format(filename, STATUS_MODIFIED)
                    cur.execute("UPDATE Files SET Status=? WHERE Hash=?",
                                (STATUS_MODIFIED, row[1],))
                    cur.execute("UPDATE Files SET Hash=? WHERE Hash=?",
                                (fhash, row[1],))
            else:
                print("File {}: {}").format(filename, STATUS_NEW)
                cur.execute("INSERT INTO Files(Filename, Hash, Status) VALUES(?, ?, ?)", (filename, fhash, STATUS_NEW,))

    if con:
        con.close()


if __name__ == "__main__":
    main(sys.argv[1:])
