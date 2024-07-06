local file_manager = {}

function file_manager.read(path)
  local file, error_msg, error_no = io.open(path, "rb")

  local bytes = nil
  if file then
    bytes = file:read("a")
    file:close()
  else
    io.stderr:write(string.format("[error] %s : %d", error_msg, error_no))
  end

  return bytes
end

function file_manager.write(path, bytes)
  local file, error_msg, error_no = io.open(path, "wb")

  if file then
    file:write(bytes)
    file:close()
  else
    io.stderr:write(string.format("[error] %s : %d", error_msg, error_no))
  end
end

return file_manager
