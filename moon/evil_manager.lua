#! /usr/bin/env lua

local argparse = require("argparse")
local sqlite   = require("lsqlite3")

local file_manager = require("file_manager")

local parser = argparse()
  :name "evil_manager"
  :description "manage evil databse"
  :epilog "find more @ https://github.com/7m45h/evil_manager"

parser:argument()
  :name "mode"
  :description "n: new table a: add l: list all e: edit d: delete o: toml output"
  :choices { 'n', 'a', 'l', 'e', 'd', 'o' }

local args = parser:parse()

local db = sqlite.open("../evil.db")

local function create_table()
  db:execute("CREATE TABLE IF NOT EXISTS movies(imdb TEXT PRIMARY KEY, name TEXT, year INTEGER, hash TEXT NULL, poster BLOB NULL)")
end

local function add_movie()
  print("[?]")
  io.write("    imdb: ")
  local imdb = io.read()
  local stmt = db:prepare("SELECT imdb, name, year FROM movies WHERE imdb=?")
  stmt:bind(1, imdb)
  local stmt_status = stmt:step()
  if stmt_status == sqlite.ROW then
    local existing_row = stmt:get_named_values()
    stmt:finalize()
    print("\n[!] allready exists")
    print(string.format("    imdb: %s", existing_row.imdb))
    print(string.format("    name: %s", existing_row.name))
    print(string.format("    year: %d", existing_row.year))

  elseif stmt_status == sqlite.DONE then
    stmt:finalize()
    io.write("    name: ")
    local name = io.read()
    io.write("    year: ")
    local year = io.read()
    io.write("    hash: ")
    local hash = string.upper(io.read())
    io.write("    poster_path: ")
    local poster_path = io.read()

    print("\n[!] summary")
    print(string.format("    imdb: %s", imdb))
    print(string.format("    name: %s", name))
    print(string.format("    year: %d", year))
    print(string.format("    hash: %s", hash))
    print(string.format("    imge: %s", poster_path))

    local poster_bytes = file_manager.read(poster_path)

    if poster_bytes then
      io.write("[?] write to db (y/N): ")
      local write = io.read()
      if write == 'y' then
        stmt = db:prepare("INSERT INTO movies VALUES (?, ?, ?, ?, ?)")
        stmt:bind(1, imdb)
        stmt:bind(2, name)
        stmt:bind(3, year)
        stmt:bind(4, hash)
        stmt:bind_blob(5, poster_bytes)
        stmt_status = stmt:step()
        if stmt_status ~= sqlite.DONE then
          print("[!] add movie failed")
        end
        stmt:finalize()
      else
        print("\n[!] did not wrote to db")
      end
    end
  end
end

local function list_movies()
  for rowid, imdb, name, year, hash in db:urows("SELECT rowid, imdb, name, year, hash FROM movies") do
    print(string.format("[%04d]  %-10s  %-55s  %4d  %s", rowid, imdb, name, year, hash))
  end
end

local function edit_movie()
  for rowid, imdb, name, year in db:urows("SELECT rowid, imdb, name, year FROM movies") do
    print(string.format("[%04d]  %-10s  %-55s  %4d", rowid, imdb, name, year))
  end

  io.write("\n[?] rowid: ")
  local rowid = io.read()
  local stmt = db:prepare("SELECT imdb, name, year, hash, poster FROM movies WHERE rowid=?")
  stmt:bind(1, rowid)
  local stmt_status = stmt:step()
  if stmt_status == sqlite.ROW then
    local existing_row = stmt:get_named_values()
    stmt:finalize()
    io.write("    imdb: ")
    local imdb = io.read()
    io.write("    name: ")
    local name = io.read()
    io.write("    year: ")
    local year = io.read()
    io.write("    hash: ")
    local hash = string.upper(io.read())
    io.write("    poster_path: ")
    local poster_path = io.read()

    if imdb == '' then imdb = existing_row.imdb end
    if name == '' then name = existing_row.name end
    if year == '' then year = existing_row.year end
    if hash == '' then hash = existing_row.hash end

    local poster_bytes
    if poster_path == '' then
      poster_bytes = existing_row.poster
    else
      poster_bytes = file_manager.read(poster_path)
    end

    print("\n[!] summary")
    print(string.format("    imdb: %s -> %s", existing_row.imdb, imdb))
    print(string.format("    name: %s -> %s", existing_row.name, name))
    print(string.format("    year: %d -> %d", existing_row.year, year))
    print(string.format("    hash: %s -> %s", existing_row.hash, hash))

    io.write("\n[?] edit (y/N): ")
    local edit = io.read()
    if edit == 'y' then
      stmt = db:prepare("UPDATE movies SET imdb=?, name=?, year=?, hash=?, poster=? WHERE rowid=?")
      stmt:bind(1, imdb)
      stmt:bind(2, name)
      stmt:bind(3, year)
      stmt:bind(4, hash)
      stmt:bind_blob(5, poster_bytes)
      stmt:bind(6, rowid)
      stmt_status = stmt:step()
      stmt:finalize()
      if stmt_status == sqlite.DONE then
        print("[!] edited")
      else
        print("[!] error not edited")
      end
    else
      print("[!] not edited")
    end
  else
    stmt:finalize()
    print("[!] id not found")
  end
end

local function delete_movie()
  io.write("[?] rowid: ")
  local rowid = io.read()
  local stmt = db:prepare("SELECT imdb, name, year FROM movies WHERE rowid=?")
  stmt:bind(1, rowid)
  local stmt_status = stmt:step()
  if stmt_status == sqlite.ROW then
    local existing_row = stmt:get_named_values()
    stmt:finalize()
    print(string.format("[!] %s %s %d", existing_row.imdb, existing_row.name, existing_row.year))
    io.write("[?] delete (y/N): ")
    local delete = io.read()
    if delete == 'y' then
      stmt = db:prepare("DELETE FROM movies WHERE rowid=?")
      stmt:bind(1, rowid)
      stmt_status = stmt:step()
      stmt:finalize()
      if stmt_status == sqlite.DONE then
        print("[!] done")
      else
        print("[!] deletion failed")
      end
    end
  else
    stmt:finalize()
    print("[!] movie not found")
  end
end

local function export_all_movies()
  local toml_output = ''
  for imdb, name, year, poster_bytes in db:urows("SELECT imdb, name, year, poster FROM movies ORDER BY name") do
    toml_output = toml_output .. string.format('[[movies]]\nimdb = "%s"\nname = "%s"\nyear = "%d"\n', imdb, name, year)
    file_manager.write(string.format("../outputs/%s.jpg", imdb), poster_bytes)
  end
  file_manager.write("../movies.toml", toml_output)
end

local modes = {
  n = create_table,
  a = add_movie,
  l = list_movies,
  e = edit_movie,
  d = delete_movie,
  o = export_all_movies
}

local action = modes[args.mode]

if action then
  action()
else
  print("[!] undefined mode")
end

db:close()
