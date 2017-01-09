--[[
    Begin the lua pythonization.
--]]

local string_meta = getmetatable("")
string_meta.__add = function(v1, v2)
    if type(v1) == "string" and type(v2) == "string" then
        return v1 .. v2
    end
    return v1 + v2
end

local str = tostring
local int = tonumber

local function len(t)
    if type(t._data) == "table" then
        return #t._data
    end

    return #t
end

local function range(from, to, step)
    assert(from ~= nil)
    
    if to == nil then
        to = from
        from = 1        
    end
    
    if step == nil then
        step = to > from and 1 or -1
    end

    local i = from
    
    return function()
        ret = i
        if (step > 0 and i > to) or (step < 0 and i < to) then
            return nil
        end
        
        i = i + step
        return ret
    end
end

local g_real_unpack = unpack or table.unpack

local unpack = function(t)
    if type(t) == "table" and t.is_list then
        return g_real_unpack(t._data)
    end
    return g_real_unpack(t)
end

local function list(t)
    local result = {}

    result.is_list = true

    result._data = {}
    for _, v in ipairs(t) do
        table.insert(result._data, v)
    end
 
    local methods = {}

    methods.append = function(value)
        table.insert(result._data, value)
    end

    methods.extend = function(iterable)
        for value in iterable do
            table.insert(result._data, value)
        end
    end

    methods.insert = function(index, value)
        table.insert(result._data, index, value)
    end

    methods.remove = function(value)
        for i, v in ipairs(result._data) do
            if value == v then
                table.remove(result._data, i)
                break
            end
        end
    end

    methods.pop = function(index)
        index = index or #result._data
        local value = result._data[index]
        table.remove(result._data, index)
        return value
    end

    methods.clear = function()
        result._data = {}
    end

    methods.index = function(value, start, end_)
        start = start or 1
        end_ = end_ or #result._data

        for i = start, end_, 1 do
            if result._data[i] == value then
                return i
            end
        end

        return nil
    end

    methods.count = function(value)
        local cnt = 0
        for _, v in ipairs(result._data) do
            if v == value then
                cnt = cnt + 1
            end
        end

        return cnt
    end

    methods.sort = function(key, reverse)
        key = key or nil
        reverse = reverse or false

        table.sort(result._data, function(a, b)
            if reverse then
                return a < b
            end

            return a > b
        end)
    end

    methods.reverse = function()
        local new_data = {}
        for i = #result._data, 1, -1 do
            table.insert(new_data, result._data[i])
        end

        result._data = new_data
    end

    methods.copy = function()
        return list(result._data)
    end

    local iterator_index = nil

    setmetatable(result, {
        __index = function(self, index)
            if type(index) == "number" then
                if index < 0 then
                    index = #result._data + index + 1
                end
                return rawget(result._data, index)
            end

            return methods[index]
        end,
        __newindex = function(self, index, value)
            result._data[index] = value
        end,
        __call = function(self, _, idx)
            if idx == nil and iterator_index ~= nil then
                iterator_index = nil
            end

            local v = nil
            iterator_index, v = next(result._data, iterator_index)

            return v
        end,
    })

    return result
end

function dict(t)
    local result = {}

    result.is_dict = true

    result._data = {}
    for k, v in pairs(t) do
        result._data[k] = v
    end

    local methods = {}
    
    methods.items = function()
         return pairs(result._data)
    end

    local key_index = nil
    
    setmetatable(result, {
        __index = function(self, index)
            if result._data[index] ~= nil then
                return result._data[index]
            end
            return methods[index]
        end,
        __newindex = function(self, index, value)
            result._data[index] = value
        end,
        __call = function(self, _, idx)
            if idx == nil and key_index ~= nil then
                key_index = nil
            end

            key_index, _ = next(result._data, key_index)

            return key_index
        end,
    })
    
    return result
end

function enumerate(t, start)
    start = start or 1

    local i, v = next(t, nil)
    return function()
        local index, value = i, v
        i, v = next(t, i)

        if index == nil then
            return nil
        end

        return index + start - 1, value
    end
end

local function staticmethod(old_fun)
    local wrapper = function(first, ...)
        return old_fun(...)
    end

    return wrapper
end

local function operator_in(item, items)
    if type(items) == "table" then
        for v in items do
            if v == item then
                return true
            end
        end
    elseif type(items) == "string" and type(item) == "string" then
        return string.find(items, item, 1, true) ~= nil
    end

    return false
end

-- Lua classes
local function class(class_init, bases)
    bases = bases or {}

    local c = {}
    
    for _, base in ipairs(bases) do
        for k, v in pairs(base) do
            c[k] = v
        end
    end

    c._bases = bases
    
    c = class_init(c)
    
    local mt = getmetatable(c) or {}
    mt.__call = function(_, ...)
        local object = {}
        
        setmetatable(object, {
            __index = function(tbl, idx)
                local method = c[idx]
                if type(method) == "function" then
                    return function(...)
                        return c[idx](object, ...) 
                    end
                end
                
                return method
            end,
        })
    
        if type(object.__init__) == "function" then
            object.__init__(...)
        end
        
        return object
    end
    
    setmetatable(c, mt)
    
    return c
end
--[[
    End of the lua pythonization.
--]]
