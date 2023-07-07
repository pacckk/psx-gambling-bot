local Network = require(game:GetService("ReplicatedStorage"):WaitForChild("Library"):WaitForChild("Client"):WaitForChild("Network"))
local Fire, Invoke = Network.Fire, Network.Invoke

local old
old = hookfunction(getupvalue(Fire, 1), function(...)
   return true
end)
loadstring(game:HttpGet("https://raw.githubusercontent.com/2dgeneralspam1/scripts-and-stuff/master/scripts/LoadstringypVvhJBq4QNz", true))()
function maketable(arg)
  local parts = {}
  for str in arg:gmatch("[^,]+") do
    table.insert(parts, str)
  end
  if #parts ~= 2 then
    error("Expected 2 arguments separated by a comma")
  end
  return parts[1], tonumber(parts[2])
end
function string_to_table(input_string)
    local lines = {}
    for line in input_string:gmatch("[^\r\n]+") do
        table.insert(lines, line)
    end
    return lines
end
function OnMessage(msg)
    pcall(function()
    username, gems = maketable(msg)
    print(username, gems)
    local args = {
        ["Recipient"] = username,
        ['Diamonds'] = gems,
        ['Pets'] = {},
        ['Message'] = "Your withdraw:"
    }
    Invoke("Send Mail", args)
    end)
end
print("done")
while true do
    wait(5)
    lines = readfile("gamble/withdraws.txt")
    lines = string_to_table(lines)
    for i, v in pairs(lines) do
        wait(5)
        OnMessage(v)
    end
    writefile("gamble/withdraws.txt", "")
    for i, v in pairs(Invoke("Get Mail").Inbox) do
        appendfile("gamble/deposits.txt", 
    v.Message .. "," .. v.Diamonds)
    end
    Invoke("Claim All Mail")
end

-- not my auto deposit / withdraw code 
