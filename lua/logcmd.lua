#!/usr/bin/lua

local nixio = require "nixio"
local params = {...}

function os.capture(cmd, raw)
  local f = assert(io.popen(cmd, 'r'))
  local s = assert(f:read('*a'))
  f:close()
  if raw then return s end
  --s = string.gsub(s, '^%s+', '')
  --s = string.gsub(s, '%s+$', '')
  s = string.gsub(s, '[\n\r]+', ' ')
  return s
end

if params[1] then
  nixio.syslog("info", os.capture(params[1]))
end
