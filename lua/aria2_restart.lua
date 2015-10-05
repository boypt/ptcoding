#!/usr/bin/lua

local json = require('json')
require ("json.rpc")
local nixio = require("nixio")


local url = "http://localhost:6800/jsonrpc"
local info = ""

rst,err = json.rpc.call(url, "aria2.getVersion")
if rst then
    info = "aria2: " .. rst["version"]
else
    nixio.syslog("err", "aria2 not running")
    do return end
end

rst,err = json.rpc.call(url, "aria2.tellActive")
if rst ~= nil and table.getn(rst) > 0 then
    info = info .. (" Running " .. table.getn(rst) .. " jobs")
else
    os.execute("/etc/init.d/aria2 restart")
    info = info .. " idle, restared"
end

nixio.syslog("info", info)

