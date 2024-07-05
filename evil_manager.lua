#! /usr/bin/env lua

local argparse = require 'argparse'
local sqlite   = require 'lsqlite3'

local parser = argparse()
  :name 'evil_manager'
  :description 'manage evil databse'
  :epilog 'find more @ https://github.com/7m45h/evil_manager'

parser:argument()
  :name 'mode'
  :description 'n: new table a: add l: list all e: edit d: delete o: toml output'
  :choices { 'n', 'a', 'l', 'e', 'd', 'o' }

local args = parser:parse()

local db = sqlite.open('./evil.db')

local function listMovies()
  for rowid, imdb, name, year, hash in db:urows 'SELECT rowid, imdb, name, year, hash FROM movies' do
    print(string.format('[%04d]  %-10s  %-55s  %4d  %s', rowid, imdb, name, year, hash))
  end
end

local modes = {
  l = listMovies
}

local action = modes[args.mode]

if action then
  action()
else
  print '[!] undefined mode'
end

db:close()
