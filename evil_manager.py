#! /usr/bin/env python

import string
import sqlite3
import argparse

PARSER = argparse.ArgumentParser(description="manage evil databse")
PARSER.add_argument("mode", choices=['n', 'a', 'l', 'e', 'd', 'o'], help="n: new table a: add l: list all e: edit d: delete o: toml output")
ARGS = PARSER.parse_args()

CON = sqlite3.connect("./evil.db")
CUR = CON.cursor()

def createTable():
    CUR.execute("CREATE TABLE IF NOT EXISTS movies(imdb TEXT PRIMARY KEY, name TEXT, year INTEGER, hash TEXT NULL, poster BLOB NULL)")
    CON.commit()
    print("[!] done")

def addMovie():
    print("[?]")
    imdb = input("    imdb: ")
    existingRow = CUR.execute("SELECT imdb, name, year FROM movies WHERE imdb=?", (imdb,)).fetchone()
    if existingRow is None:
        name = input("    name: ")
        year = input("    year: ")
        hash = input("    hash: ").upper()
        posterPath = input("    poster: ")
        print("[!] summary")
        print(f"    imdb: {imdb}")
        print(f"    name: {name}")
        print(f"    year: {year}")
        print(f"    hash: {hash}")
        print(f"    imge: {posterPath}")

        posterBytes = None

        try:
            with open(posterPath, "rb") as posterFile:
                posterBytes = posterFile.read()
        except FileNotFoundError:
            print(f"[!] poster path: {posterPath} does not exist")
        except Exception as e:
            print(f"[!] error: {e}")

        if posterBytes is None:
            print("[!] read poster failed")
        else:
            write = input("[?] write to db (y/N): ")
            if write == "y":
                CUR.execute("INSERT INTO movies VALUES (?, ?, ?, ?, ?)", (imdb, name, year, hash, posterBytes))
                CON.commit()
            else:
                print("\n[!] did not wrote to db")

    else:
        print("\n[!] allready exists")
        print(f"\n    imdb: {existingRow[0]}")
        print(f"\n    name: {existingRow[1]}")
        print(f"\n    year: {existingRow[2]}")

def listAllMovies():
    for row in CUR.execute("SELECT rowid, imdb, name, year, hash FROM movies").fetchall():
        print(f"[{row[0]:04d}]  {row[1]: <10s}  {row[2]:.<55s}  {row[3]:4d}  {row[4]}")

def editMovie():
    for row in CUR.execute("SELECT rowid, imdb, name FROM movies").fetchall():
        print(f"[{row[0]:04d}] {row[1]} {row[2]}")

    rowID = input("\n[?] rowid: ")
    row = CUR.execute("SELECT imdb, name, year, hash, poster FROM movies WHERE rowid=?", (rowID,)).fetchone()

    if row is None:
        print("[!] id not found")
    else:
        imdb = row[0] if not (imdb := input("    imdb: ")) else imdb
        name = row[1] if not (name := input("    name: ")) else name
        year = row[2] if not (year := input("    year: ")) else year
        hash = row[3] if not (hash := input("    hash: ")) else hash.upper()
        posterPath = input("    poster: ")

        posterBytes = None

        if not posterPath:
            posterBytes = row[4]
        else:
            try:
                with open(posterPath, "rb") as posterFile:
                    posterBytes = posterFile.read()
            except FileNotFoundError:
                print(f"[!] poster path: {posterPath} does not exist")
            except Exception as e:
                print(f"[!] error: {e}")

        print("\n[!] summary")
        print(f"    imdb: {row[0]} -> {imdb}")
        print(f"    name: {row[1]} -> {name}")
        print(f"    year: {row[2]} -> {year}")
        print(f"    hash: {row[3]} -> {hash}")

        edit = input("\n[?] edit (y/N): ")
        if edit == 'y':
            CUR.execute("UPDATE movies SET imdb=?, name=?, year=?, hash=?, poster=? WHERE rowid=?", (imdb, name, year, hash, posterBytes, rowID))
            CON.commit()
            print("[!] done")
        else:
            print("[!] did not edited")

def deleteMovie():
    imdb = input("[?] imdb: ")
    row = CUR.execute("SELECT rowid, name, year FROM movies WHERE imdb=?", (imdb,)).fetchone()
    print("[!]")
    print(f"[{row[0]}]\t{row[1]}\t{row[2]}")
    delete = input("[?] delete (y/N): ")

    if delete == "y":
        CUR.execute("DELETE FROM movies WHERE imdb=?", (imdb,))
        CON.commit()
        print("[!] done")
    else:
        print("[!] did not deleted")

def exportDB():
    try:
        with open("movies.toml", "w") as tomlFile:
            for row in CUR.execute("SELECT imdb, name, year, hash, poster FROM movies ORDER BY name").fetchall():
                imdb = row[0]
                name = row[1]
                year = row[2]
                hash = row[3]
                posterBytes = row[4]

                tomlFile.write(f"""[[movies]]\nimdb = "{imdb}"\nname = "{name}"\nyear = "{year}"\n""")
                with open(f"./outputs/{imdb}.jpg", "wb") as posterFile:
                    posterFile.write(posterBytes)
    except Exception as e:
        print(f"[!] error: {e}")

MODES = {
    'n': createTable,
    'a': addMovie,
    'l': listAllMovies,
    'e': editMovie,
    'd': deleteMovie,
    'o': exportDB
}

try:
    action = MODES[ARGS.mode]
except KeyError:
    print("[!] undefined mode")
except Exception as e:
    print(f"[!] error: {e}")

action()

CON.close()
exit()
