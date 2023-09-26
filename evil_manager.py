#! /usr/bin/env python

import string
import sqlite3
import argparse

_parser = argparse.ArgumentParser(description="manage evil databse")
_parser.add_argument("mode", choices=["n", "a", "l", "d", "o"], help="n: new table a: add l: list all d: delete o: html output")
args = _parser.parse_args()

_con = sqlite3.connect("./evil.db")
_cur = _con.cursor()

def newDatabase():
    _cur.execute("CREATE TABLE IF NOT EXISTS movies(imdb TEXT PRIMARY KEY, name TEXT, year INTEGER, hash TEXT NULL, poster BLOB NULL)")
    _con.commit()
    print("[!] done")

def addNew():
    print("[?]")
    imdb = input("    imdb: ")
    existing_row = _cur.execute("SELECT imdb, name, year FROM movies WHERE imdb=?", (imdb,)).fetchone()
    if existing_row is None:
        name = input("    name: ")
        year = input("    year: ")
        hash = input("    hash: ").upper()
        poster = input("    poster: ")
        print("[!] summary")
        print(f"    hash: {imdb}")
        print(f"    name: {name}")
        print(f"    year: {year}")
        print(f"    imdb: {hash}")
        print(f"    imge: {poster}")

        with open(poster, "rb") as image:
            poster_bytes = image.read();

        write = input("[?] write to db (y/n): ")
        if write == "y":
            _cur.execute("INSERT INTO movies VALUES (?, ?, ?, ?, ?)", (imdb, name, year, hash, poster_bytes))
            _con.commit()
        else:
            print("\n[!] did not wrote to db")
    else:
        print("\n[!] allready exists")
        print(f"\n    imdb: {existing_row[0]}")
        print(f"\n    name: {existing_row[1]}")
        print(f"\n    year: {existing_row[2]}")

def listAll():
    for row in _cur.execute("SELECT rowid, imdb, name, year, hash FROM movies").fetchall():
        print(f"[{row[0]:04d}]  {row[1]}  {row[2]:.<45s}  {row[3]:4d}  {row[4]}")

def deleteRow():
    imdb = input("[?] imdb: ")
    row = _cur.execute("SELECT rowid, name, year FROM movies WHERE imdb=?", (imdb,)).fetchone()
    print("[!]")
    print(f"[{row[0]}]\t{row[1]}\t{row[2]}")
    delete = input("[?] delete (y/n): ")

    if delete == "y":
        _cur.execute("DELETE FROM movies WHERE imdb=?", (imdb,))
        _con.commit()
        print("[!] done")
    else:
        print("[!] did not deleted")

def htmlOutput():
    for row in _cur.execute("SELECT imdb, name, year, hash, poster FROM movies ORDER BY name").fetchall():
        imdb = row[0]
        name = row[1]
        year = row[2]
        hash = row[3]
        poster_bytes = row[4]

        if poster_bytes is None:
            poster_path = "./images/placeholder.jpg"
        else:
            poster_path = f"./images/{imdb}.jpg"
            with open(f"./outputs/{imdb}.jpg", "wb") as image:
                image.write(poster_bytes)
        
        print(f"""          <a href="https://www.imdb.com/title/{imdb}/" target="_blank">\n            <img src="{poster_path}" alt="{name} {year}" title="{name} {year}" loading="lazy">\n          </a>""")

if args.mode == "n":
    newDatabase()
elif args.mode == "d":
    deleteRow()
elif args.mode == "a":
    addNew()
elif args.mode == "o":
    htmlOutput()
else:
    listAll()

_con.close()
exit()
