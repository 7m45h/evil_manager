#! /usr/bin/env python

import string
import sqlite3
import argparse

PARSER = argparse.ArgumentParser(description="manage evil databse")
PARSER.add_argument("mode", choices=['n', 'a', 'l', 'e', 'd', 'o'], help="n: new table a: add l: list all e: edit d: delete o: toml output")
ARGS = PARSER.parse_args()

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
    row = CUR.execute("SELECT imdb, name, year, hash, poster FROM movies WHERE rowid=?", (rowid,)).fetchone()

    if row is None:
        print("[!] id not found")
    else:
        imdb = row[0] if not (imdb := input("    imdb: ")) else imdb
        name = row[1] if not (name := input("    name: ")) else name
        year = row[2] if not (year := input("    year: ")) else year
        hash = row[3] if not (hash := input("    hash: ")) else hash.upper()
        poster_path = input("    poster: ")

        if not poster_path:
            poster_bytes = row[4]
        else:
            try:
                image_file = open(poster_path, "rb")
                poster_bytes = image_file.read()
                image_file.close()
            except FileNotFoundError:
                print(f"[!] poster path: {poster_path} does not exist")
            except Exception as e:
                print(f"[!] error: {e}")

        print("\n[!] summary")
        print(f"    imdb: {row[0]} -> {imdb}")
        print(f"    name: {row[1]} -> {name}")
        print(f"    year: {row[2]} -> {year}")
        print(f"    hash: {row[3]} -> {hash}")

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

if ARGS.mode == 'n':
    newDatabase()
elif ARGS.mode == 'a':
    addNew()
elif ARGS.mode == 'l':
    listAll()
elif ARGS.mode == 'e':
    editRow()
elif ARGS.mode == 'd':
    deleteRow()
elif ARGS.mode == 'o':
    tomlOutput()
else:
    print("[!] error")

CON.close()
exit()
