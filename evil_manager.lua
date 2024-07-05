#! /usr/bin/env lua

local argparse = require('argparse')
local sqlite   = require('lsqlite3')

local parser = argparse()
  :name 'evil_manager'
  :description 'manage evil databse'
  :epilog 'find more @ https://github.com/7m45h/evil_manager'

parser:argument()
  :name 'mode'
  :description 'n: new table a: add l: list all e: edit d: delete o: toml output'
  :choices { 'n', 'l' }

local args = parser:parse()

local db = sqlite.open('./evil.db')

local function create_table()
  db:execute('CREATE TABLE IF NOT EXISTS movies(imdb TEXT PRIMARY KEY, name TEXT, year INTEGER, hash TEXT NULL, poster BLOB NULL)')
end

local function list_movies()
  for rowid, imdb, name, year, hash in db:urows('SELECT rowid, imdb, name, year, hash FROM movies') do
    print(string.format('[%04d]  %-10s  %-55s  %4d  %s', rowid, imdb, name, year, hash))
  end
end

local modes = {
  n = create_table,
  l = list_movies
}

local action = modes[args.mode]

if action then
  action()
else
  print('[!] undefined mode')
end

db:close()
