#! /usr/bin/env python

import string
import sqlite3
import argparse

PARSER = argparse.ArgumentParser(description="manage evil databse")
PARSER.add_argument("mode", choices=['n', 'a', 'l', 'e', 'd', 'o'], help="n: new table a: add l: list all e: edit d: delete o: toml output")
args = PARSER.parse_args()

CON = sqlite3.connect("./evil.db")
CUR = CON.cursor()

def newDatabase():
    CUR.execute("CREATE TABLE IF NOT EXISTS movies(imdb TEXT PRIMARY KEY, name TEXT, year INTEGER, hash TEXT NULL, poster BLOB NULL)")
    CON.commit()
    print("[!] done")

def addNew():
    print("[?]")
    imdb = input("    imdb: ")
    existing_row = CUR.execute("SELECT imdb, name, year FROM movies WHERE imdb=?", (imdb,)).fetchone()
    if existing_row is None:
        name = input("    name: ")
        year = input("    year: ")
        hash = input("    hash: ").upper()
        poster = input("    poster: ")
        print("[!] summary")
        print(f"    imdb: {imdb}")
        print(f"    name: {name}")
        print(f"    year: {year}")
        print(f"    hash: {hash}")
        print(f"    imge: {poster}")

        with open(poster, "rb") as image:
            poster_bytes = image.read();

        write = input("[?] write to db (y/n): ")
        if write == "y":
            CUR.execute("INSERT INTO movies VALUES (?, ?, ?, ?, ?)", (imdb, name, year, hash, poster_bytes))
            CON.commit()
        else:
            print("\n[!] did not wrote to db")
    else:
        print("\n[!] allready exists")
        print(f"\n    imdb: {existing_row[0]}")
        print(f"\n    name: {existing_row[1]}")
        print(f"\n    year: {existing_row[2]}")

def listAll():
    for row in CUR.execute("SELECT rowid, imdb, name, year, hash FROM movies").fetchall():
        print(f"[{row[0]:04d}]  {row[1]: <10s}  {row[2]:.<55s}  {row[3]:4d}  {row[4]}")

def editRow():
    for row in CUR.execute("SELECT rowid, imdb, name FROM movies").fetchall():
        print(f"[{row[0]:04d}] {row[1]} {row[2]}")

    rowid = input("\n[?] rowid: ")
    row = CUR.execute("SELECT imdb, name, year, hash FROM movies WHERE rowid=?", (rowid,)).fetchone()

    if row is None:
        print("[!] id not found")
    else:
        imdb = input("    imdb: ")
        name = input("    name: ")
        year = input("    year: ")
        hash = input("    hash: ").upper()
        poster = input("    poster: ")

        with open(poster, "rb") as image:
            poster_bytes = image.read();

        print("\n[!] summary")
        print(f"    imdb: {row[0]: >42s} -> {imdb}")
        print(f"    name: {row[1]: >42s} -> {name}")
        print(f"    year: {row[2]: 42d} -> {year}")
        print(f"    hash: {row[3]: >42s} -> {hash}")
        print(f"    imge: {'current': >42s} -> {poster}")

        edit = input("\n[?] edit (y/n): ")
        if edit == 'y':
            CUR.execute("UPDATE movies SET imdb=?, name=?, year=?, hash=?, poster=? WHERE rowid=?", (imdb, name, year, hash, poster_bytes, rowid))
            CON.commit()
            print("[!] done")
        else:
            print("[!] did not edited")

def deleteRow():
    imdb = input("[?] imdb: ")
    row = CUR.execute("SELECT rowid, name, year FROM movies WHERE imdb=?", (imdb,)).fetchone()
    print("[!]")
    print(f"[{row[0]}]\t{row[1]}\t{row[2]}")
    delete = input("[?] delete (y/n): ")

    if delete == "y":
        CUR.execute("DELETE FROM movies WHERE imdb=?", (imdb,))
        CON.commit()
        print("[!] done")
    else:
        print("[!] did not deleted")

def tomlOutput():
    with open("movies.toml", "w") as tFile:
        for row in CUR.execute("SELECT imdb, name, year, hash, poster FROM movies ORDER BY name").fetchall():
            imdb = row[0]
            name = row[1]
            year = row[2]
            hash = row[3]
            poster_bytes = row[4]

            tFile.write(f"""[[movies]]\nimdb = "{imdb}"\nname = "{name}"\nyear = "{year}"\n""")
            with open(f"./outputs/{imdb}.jpg", "wb") as pFile:
                pFile.write(poster_bytes)

if args.mode == 'n':
    newDatabase()
elif args.mode == 'a':
    addNew()
elif args.mode == 'l':
    listAll()
elif args.mode == 'e':
    editRow()
elif args.mode == 'd':
    deleteRow()
elif args.mode == 'o':
    tomlOutput()
else:
    print("[!] error")

CON.close()
exit()
