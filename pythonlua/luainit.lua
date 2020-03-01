--[[
    Begin the lua pythonization.
--]]
-- for type comparisons
float = "number"

-- overwriting type so we can type dicts and lists etc.
rawtype = type
function type(obj)
    local t = rawtype(obj)
    if (t == 'table') then
        local mt = getmetatable(obj)
        if (mt ~= nil) then            
            if (mt.__type and rawtype(mt.__type) == "function") then
                return getmetatable(obj).__type(obj)
            elseif (mt.__type and rawtype(mt.__type) == "table") then
                return getmetatable(obj).__type
            end
            return getmetatable(obj).__type or t
        end
    end
    return t
end

function isinstance(obj,typ)
    if (typ == int) then
        typ = "number"
    elseif (typ == str) then
        typ = "string"
    end
    if rawtype(typ) == "table" then
        -- here we should also check for types of _bases
        ret = getmetatable(typ).__type or "table"
        return type(obj) == ret
    end
    return type(obj) == typ
end

local string_meta = getmetatable("")
string_meta.__add = function(v1, v2)
    if type(v1) == "string" and type(v2) == "string" then
        return v1 .. v2
    end
    return v1 + v2
end

local g_real_unpack = unpack or table.unpack

unpack = function(t)
    if type(t) == list then
        return g_real_unpack(t._data)
    end
    return g_real_unpack(t)
end

abs = math.abs
ascii = string.byte
chr = string.char
int = tonumber
str = tostring

function all(iterable)
    for element in iterable do
        if not element then
            return false
        end
    end
    return true
end

function any(iterable)
    for element in iterable do
        if element then
            return true
        end
    end
    return false
end

function bool(x)
    if x == false or x == nil or x == 0 then
        return false
    end

    if type(x) == list or type(x) == dict then
        return next(x._data) ~= nil
    end

    return true
end 

function callable(x)
    local x_type = type(x)
    if x_type == "function" then
        return true
    end
    if x_type == "table" then
        local meta = getmetatable(x)
        return type(meta.__call) == "function" 
    end

    return false
end

function divmod(a, b)
    local res = { math.floor(a / b), math.fmod(a, b) }
    return unpack(res)
end

function len(t)
    if type(t._data) == "table" then
        return #t._data
    end

    return #t
end

function range(from, to, step)
    assert(from ~= nil)
    
    if to == nil then
        to = from
        from = 0        
    end

    step = step or 1

    local i = from
    
    return function()
        ret = i
        if (step > 0 and i >= to) or (step < 0 and i <= to) then
            return nil
        end
        
        i = i + step
        return ret
    end
end

function enumerate(t, start)
    start = start or 0

    local data = t
    if type(t) == list then
        data = t._data
    end

    local i, v = next(data, nil)
    return function()
        local index, value = i, v
        i, v = next(data, i)

        if index == nil then
            return nil
        end

        return index + start - 1, value
    end
end

list = {}
setmetatable(list, {
    __call = function(_, t)
        local result = {}

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

        methods.index = function(value, start, enda)
            start = start or 1
            enda = enda or #result._data

            for i = start, enda, 1 do
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
                        index = #result._data + index
                    end
                    return rawget(result._data, index + 1)
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
            __type = list
        })

        return result
    end,
    __type = list,
    __tostring = function(self)
        return "list"
    end
})

dict = {}
setmetatable(dict, {
    __call = function(_, t)
        local result = {}

        result._data = {}
        for k, v in pairs(t) do
            result._data[k] = v
        end

        local methods = {}

        local key_index = nil

        methods.clear = function()
            result._data = {}
        end

        methods.copy = function()
            return dict(result._data)
        end

        methods.get = function(key, default)
            default = default or nil
            if result._data[key] == nil then
                return default
            end

            return result._data[key]
        end

        methods.items = function()
            return pairs(result._data)
        end

        methods.keys = function()
            return function(self, idx, _) 
                if idx == nil and key_index ~= nil then
                    key_index = nil
                end

                key_index, _ = next(result._data, key_index)
                return key_index
            end
        end

        methods.pop = function(key, default)
            default = default or nil
            if result._data[key] ~= nil then
                local value = result._data[key]
                result._data[key] = nil 
                return key, value
            end

            return key, default
        end

        methods.popitem = function()
            local key, value = next(result._data)
            if key ~= nil then
                result._data[key] = nil
            end

            return key, value
        end

        methods.setdefault = function(key, default)
            if result._data[key] == nil then
                result._data[key] = default
            end

            return result._data[key]
        end

        methods.update = function(t)
            assert(type(t) == dict)

            for k, v in t.items() do
                result._data[k] = v
            end
        end

        methods.values = function()
            return function(self, idx, _) 
                if idx == nil and key_index ~= nil then
                    key_index = nil
                end

                key_index, value = next(result._data, key_index)
                return value
            end
        end
        
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
            __type = dict
        })
        
        return result
    end,
    __type = dict,
    __tostring = function(self)
        return "dict"
    end
})

function staticmethod(old_fun)
    return old_fun
end

function operator_in(item, items)
    if type(items) == list or type(items) == dict then
        for v in items do
            if v == item then
                return true
            end
        end
    elseif type(items) == "string" and type(item) == "string" then
        return string.find(items, item, 1, true) ~= nil
    elseif rawtype(items) == "table" then
        if callable(getmetatable(items).__in) then
            return getmetatable(items).__in(items,item)
        end
    end
    return false
end

-- Lua classes
function class(class_init, name, bases, mtmethods, properties)
    bases = bases or {}

    local c = {}
    c.properties = {}
    for _, base in ipairs(bases) do
        for k, v in pairs(base) do
            c[k] = v
        end
    end

    c._bases = bases
    
    c = class_init(c)
    
    for k,v in pairs(properties) do
        c.properties[k] = v
    end
    
    local mt = getmetatable(c) or {}
    mt.__call = function(_, ...)
        local object = {}

        nmt = {}
        nmt.__type = c
        for k,v in pairs(c.mtmethods) do
            nmt[k] = c[v]
        end
        nmt.__index = function(tbl, idx)
            local attr = c[idx]
            if (c.properties[idx]) then
                return attr.gfunc(tbl)
            end
            return attr
        end
        nmt.__newindex = function(tbl, idx, new)
            local attr = c[idx]
            if (c.properties[idx]) then
                attr.sfunc(tbl,new)
            else
                rawset(tbl,idx,new)
            end
        end
        setmetatable(object, nmt)
        if type(object.__init__) == "function" then
            object:__init__(...)
        end
        return object
    end
    c.mtmethods = mtmethods
    mt.__type = c
    mt.__tostring = function() 
        return name   -- perhaps it is better if the type table is not the main object, but instead a separate table? the __tostring of the main object might be confusing.
    end
    setmetatable(c, mt)
    
    return c
end
-- properties implemented by class object / decorator. Requires as well a properties list
-- on the main class for __index and __newindex referral.
property = class(function(property)
    function property.__init__(self,gfunc,sfunc)
        rawset(self,"gfunc",gfunc)
        rawset(self,"sfunc",sfunc)
    end
    function property.getter(self,gfunc)
        rawset(self,"gfunc",gfunc)
        return self
    end
    function property.setter(self,sfunc)
        rawset(self,"sfunc",sfunc)
        return self
    end
    return property
end, "property", {}, {}, {})

--[[
    End of the lua pythonization.
--]]
