local sqlite = require("lsqlite3")

local base_manager = {}

function base_manager.get_row(db, select, ...)
  local results = nil
  local stmt = db:prepare(select)
  local stmt_status = stmt:bind_values(...)

  if stmt_status == sqlite.OK then
    local row_idx = 1
    results = {}
    stmt_status = stmt:step()

    repeat
      results[row_idx] = stmt:get_named_values()
      stmt_status = stmt:step()
      row_idx = row_idx + 1
    until stmt_status ~= sqlite.ROW

    if stmt_status == sqlite.ERROR then
      io.stderr:write(string.format("[error] %s\n", db:errmsg()))
    elseif stmt_status ~= sqlite.DONE then
      io.stderr:write(string.format("[exception] number: %d\n", stmt_status))
    end

  else
    io.stderr:write(string.format("[exception] number: %d\n", stmt_status))
  end

  stmt:finalize()
  return results
end

return base_manager
