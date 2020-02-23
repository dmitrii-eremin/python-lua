# Python 3 to lua translator

Python version: 3.7
Lua version: 5.3

**I want to know more about [FEATURES](#features)!**


## Changes

- The latest version includes the use of 'operator overloading', and 'properties' in [classes](#classes)
- [Type comparisons](#type) have been added
- [Try/except blocks](#tryexcept-block) have been added

## Usage

### As a standalone application
```
usage: python-lua [-h] [--show-ast] [--only-lua-init] [--no-lua-init] [IF]

Python to lua translator.

positional arguments:
  IF               A python script filename to translate it.

optional arguments:
  -h, --help       show this help message and exit
  --show-ast       Print python ast tree before code.
  --only-lua-init  Print only lua initialization code.
  --no-lua-init    Print lua code without lua init code.
```

For example: ```python3 __main__py tests/iterlist.py```

### As a packet
```python
from pythonlua.translator import Translator

...

translator = Translator()
lua_code = translator.translate(python_code)
````

For example see ```runtests.py```.


## Warning

This translator defines some python functions in lua (```len```, ```range```, ```enumerate```, ```list```, ```dict``` and other).
For list and dict it also defines most methods like ```append()``` for ```list``` and ```items()``` for ```dict```.
You can find this definitions in the file [pythonlua/luainit.lua](./pythonlua/luainit.lua).
Also this definitions will be in the output, when you run translator as a standalone application.

For example:
```
(venv) ******@****:~/Projects/python/python-lua$ python3 __main__.py tests/del.py
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

local function list(t)
    local methods = {}

    methods.append = function(value)
        table.insert(t, value)
    end

    local iterator_index = nil

    setmetatable(t, {
        __index = function(self, index)
            if type(index) == "number" and index < 0 then
                return rawget(t, #t + index + 1)
            end

            return methods[index]
        end,
        __call = function(self, _, idx)
            if idx == nil and iterator_index ~= nil then
                iterator_index = nil
            end

            local v = nil
            iterator_index, v = next(t, iterator_index)

            return v
        end,
    })
    return t
end

function dict(t)
    local methods = {}
    
    methods.items = function()
         return pairs(t)
    end

    local key_index = nil
    
    setmetatable(t, {
        __index = methods,
        __call = function(self, _, idx)
            if idx == nil and key_index ~= nil then
                key_index = nil
            end

            key_index, _ = next(t, key_index)

            return key_index
        end,
    })
    
    return t
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
local a, b, c = 1, 2, 3
print(a, b, c)
a, b = nil, nil
print(a, b, c)
c = nil
print(a, b, c)
```


## Features

### Insert lua code in the python
You can start your string with the tag `[[luacode]]` to simply insert lua code in the python. For example,

Python code:
```python
def get_summ(a, b):
    return a + b

print(get_summ(3, 5))

"""[[luacode]]
local c = 45
print(c)
"""
```

Lua code:
```lua
local function get_summ(a, b)
    return (a + b)
end
print(get_summ(3, 5))

local c = 45
print(c)
```

### Simple math:  

Python code:
```python
print(5 + 3)
print(18 - 2)
print(5 * 5)
print(64 / 2)
print(11 ** 2)
print(11 // 2)
print(11 / 2)
print(((5 + 34) ** 2 / 53) * (24 - 6 * 3))
```

Lua code:
```lua
print((5 + 3))
print((18 - 2))
print((5 * 5))
print((64 / 2))
print((math.pow(11, 2)))
print((math.floor(11 / 2)))
print((11 / 2))
print((((math.pow((5 + 34), 2)) / 53) * (24 - (6 * 3))))
```

### Bitwise operations

Python code:
```python
a = 0xFA23423
b = 0xAC23BD2
c = 0x548034D

print(a & b)
print((a & b) | c)

print(~((a & b) | c))
```

Lua code:
```lua
local a = 262288419
local b = 180501458
local c = 88605517
print((bit32.band(a, b)))
print((bit32.bor((bit32.band(a, b)), c)))
print(bit32.bnot((bit32.bor((bit32.band(a, b)), c))))
```

### Function definitions with variable arguments number and default arguments

Python code:
```python
def hello(name, age=20, nickname="", *args):
    print("Hello, my name is " + name + " and I'm " + str(age))
    print("My nickname is " + nickname)
    print(*args)

hello("John", 12, "antikiller")
hello("Josh", 45)
hello("Jane")
```

Lua code:
```lua
local function hello(name, age, nickname, ...)
    age = age or 20
    nickname = nickname or ""
    local args = list {...}
    print(((("Hello, my name is " + name) + " and I'm ") + str(age)))
    print(("My nickname is " + nickname))
    print(unpack(args))
end
hello("John", 12, "antikiller")
hello("Josh", 45)
hello("Jane")
```

### Function decorators

Python code:
```python
def strong(old_fun):
    def wrapper(*args):
        s = "<strong>" + old_fun(*args) + "</strong>"
        return s
    return wrapper

def italic(old_fun):
    def wrapper(*args):
        s = "<em>" + old_fun(*args) + "</em>"
        return s
    return wrapper

@italic
@strong
def hello(name):
    return "Hello, " + name + "!"

print(hello("John"))
```

Lua code:
```lua
local function strong(old_fun)
    local function wrapper(...)
        local args = list {...}
        local s = (("<strong>" + old_fun(unpack(args))) + "</strong>")
        return s
    end
    return wrapper
end
local function italic(old_fun)
    local function wrapper(...)
        local args = list {...}
        local s = (("<em>" + old_fun(unpack(args))) + "</em>")
        return s
    end
    return wrapper
end
local function hello(name)
    return (("Hello, " + name) + "!")
end
hello = strong(hello)
hello = italic(hello)
print(hello("John"))

```

### If/elif/else, for and while loops

Python code:
```python
a = 45
b = 0

if a > 5 and b < 34:
    print("a > 5")
    if a >= 45:
        print("a >= 45")
    else:
        print("a < 45")
elif a < 5:
    print("a < 5")
else:
    print("a == 5")

if a == 45:
    print("a == 45")

x = 100
if 50 < x < 150:
    print("50 < x < 150")
else:
    print("Something wrong.")

i = 10
while i > 0:
    print(i)
    i -= 1
```

Lua code:
```lua
local b = 0
if ((a > 5) and (b < 34)) then
    print("a > 5")
    if (a >= 45) then
        print("a >= 45")
    else
        print("a < 45")
    end
elseif (a < 5) then
    print("a < 5")
else
    print("a == 5")
end
if (a == 45) then
    print("a == 45")
end
local x = 100
if (50 < x and x < 150) then
    print("50 < x < 150")
else
    print("Something wrong.")
end
local i = 10
while (i > 0) do
    print(i)
    i = (i - 1)
end
```

### If expression

Python code:
```python
def factorial(value):
    return 1 if value == 0 else value * factorial(value - 1)

print(factorial(5))
print(factorial(10))
print(factorial(3))
print(factorial(0))

```

Lua code:
```lua
local function factorial(value)
    return (value == 0) and 1 or (value * factorial((value - 1)))
end
print(factorial(5))
print(factorial(10))
print(factorial(3))
print(factorial(0))
```

### Lists and dictionaries

Python code:
```python
a = [1, 2, 5]
b = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

c = {
    "firstname": "John",
    "lastname": "Doe",
    "age": 42,
    "children": [
        {
            "name": "Sara",
            "age": 4,
        },
    ],
}

print(a[2])
print(b[1][2])
print(c["firstname"], c["lastname"])

ch = c["children"][1]
print(ch["name"], ch["age"])
```

Lua code:
```lua
local a = list {1, 2, 5}
local b = list {list {1, 2, 3}, list {4, 5, 6}, list {7, 8, 9}}
local c = dict {["firstname"] = "John", ["lastname"] = "Doe", ["age"] = 42, ["children"] = list {dict {["name"] = "Sara", ["age"] = 4}}}
print(a[2])
print(b[1][2])
print(c["firstname"], c["lastname"])
local ch = c["children"][1]
print(ch["name"], ch["age"])
```

### Python import statement

Python code:
```python
import foo.bar
import bar as bar_ex
```

Lua code:
```lua
local bar = require "foo.bar"
local bar_ex = require "bar"
```

### Lambda functions

Python code:
```python
sqr = lambda x: x * x
print(sqr(2))
print(sqr(8))
```

Lua code:
```lua
local sqr = function(x) return (x * x) end
print(sqr(2))
print(sqr(8))
```

### Python del operator

Python code:
```python
a, b, c = 1, 2, 3
print(a, b, c)
del a, b
print(a, b, c)
del c
print(a, b, c)
```

Lua code:
```lua
local a, b, c = 1, 2, 3
print(a, b, c)
a, b = nil, nil
print(a, b, c)
c = nil
print(a, b, c)
```

### Python list and dictionary comprehensions

Python code:
```python
a = [i * j for i in range(5) for j in range(3) if i * j % 2 == 0 and i > 0 and j > 0]

for item in a:
    print(item)

b = {i: i ** 2 for i in range(5)}

for k, v in b.items():
    print(k, v)
```

Lua code:
```lua
local a = (function() local result = list {} for i in range(5) do for j in range(3) do if (((math.fmod((i * j), 2)) == 0) and (i > 0)) then result.append((i * j)) end end end return result end)()
for item in a do
    print(item)
    ::loop_label_1::
end
local b = (function() local result = dict {} for i in range(5) do result[i] = (math.pow(i, 2)) end return result end)()
for k, v in b.items() do
    print(k, v)
    ::loop_label_2::
end
```

### Classes

Python code:
```python
class Animal:
    PLANET = "Earth"

    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print("Hello, my name is: " + self.name + "!")


class Dog(Animal):
    def say_hello(self):
        print("Hello, my name is: " + self.name + "!")
        self.bark()

    def bark(self):
        print("Bark! Bark! Bark!")


sparky = Animal("Sparky")
barky = Dog("Barky")

sparky.say_hello()
barky.say_hello()

barky.bark()

print("Animal.PLANET = ", Animal.PLANET)
print("sparky.PLANET = ", sparky.PLANET)
print("barky.PLANET = ", barky.PLANET)

Animal.PLANET = "Mars"

print("Animal.PLANET = ", Animal.PLANET)
print("sparky.PLANET = ", sparky.PLANET)
```

Lua code:
```lua
local Animal = class(function(Animal)
    Animal.PLANET = "Earth"
    function Animal.__init__(self, name)
        self.name = name
    end
    function Animal.say_hello(self)
        print((("Hello, my name is: " + self.name) + "!"))
    end
    return Animal
end, {})
local Dog = class(function(Dog)
    function Dog.say_hello(self)
        print((("Hello, my name is: " + self.name) + "!"))
        self.bark()
    end
    function Dog.bark(self)
        print("Bark! Bark! Bark!")
    end
    return Dog
end, {Animal})
local sparky = Animal("Sparky")
local barky = Dog("Barky")
sparky.say_hello()
barky.say_hello()
barky.bark()
print("Animal.PLANET = ", Animal.PLANET)
print("sparky.PLANET = ", sparky.PLANET)
print("barky.PLANET = ", barky.PLANET)
Animal.PLANET = "Mars"
print("Animal.PLANET = ", Animal.PLANET)
print("sparky.PLANET = ", sparky.PLANET)
```

Operator overloading & Properties:

```python
class A:
    def __init__(self,value):
        self.v = value
    def __add__(self,other):
        return A(self.v+other.v)
    @property
    def v(self):
        return self._v
    @v.setter
    def v(self,value):
        if (value > 0):
            self._v = value
    def __str__(self):
        return str(self.v)    
a = A(3)
b = A(4)
c = a+b
print(c)
c.v = 4  # sets the value
print(c)
c.v = -1  # doesn't set the value because v <= 0.
print(c)
```
Lua code:
```lua
local A = class(function(A)
    function A.__init__(self, value)
        self.v = value
    end
    function A.__add__(self, other)
        return A((self.v + other.v))
    end
    A.v = property(function(self)
        return self._v
    end)
    A.v = A.v.setter(function(self, value)
        if (value > 0) then
            self._v = value
        end
    end)
    function A.__str__(self)
        return str(self.v)
    end
    return A
end, {}, {__add = "__add__", __tostring = "__str__"}, {v = "A.v"})
local a = A(3)
local b = A(4)
local c = (a + b)
print(c)
c.v = 4
print(c)
c.v = -1
print(c)
```
Output:
7
4
4

### Loops continue statement

Python code:
```python
for i in range(10):
    if i == 5:
        continue
    for j in range(10):
        if j == 7:
            continue
        print(i, " * ", j, " = ", i * j)
```

Lua code:
```lua
for i in range(10) do
    if (i == 5) then
        goto loop_label_1
    end
    for j in range(10) do
        if (j == 7) then
            goto loop_label_2
        end
        print(i, " * ", j, " = ", (i * j))
        ::loop_label_2::
    end
    ::loop_label_1::
end
```

### Operators `in` and `not in`

Python code:
```python
a = [1, 2, 3, 4]
b = {
    "name": "John",
    "age": 42,
}

c = "Hello, world!"

if 2 < 3:
    print("2 < 3")

print(1 in a)
print(2 in a)
print(5 in a)
print("name" in b)
print("surname" in b)
print("Hell" in c)
print("world" in c)
print("Foo" in c)
print("Hells" not in c)
```

Lua code:
```lua
local a = list {1, 2, 3, 4}
local b = dict {["name"] = "John", ["age"] = 42}
local c = "Hello, world!"
if (2 < 3) then
    print("2 < 3")
end
print((operator_in(1, a)))
print((operator_in(2, a)))
print((operator_in(5, a)))
print((operator_in("name", b)))
print((operator_in("surname", b)))
print((operator_in("Hell", c)))
print((operator_in("world", c)))
print((operator_in("Foo", c)))
print((not operator_in("Hells", c)))
```


### Type

Currently type comparisons are done using isinstance. Comparisons such as ```if type(var) is int:``` cannot be done
on basic types. They do work on lists, dicts and classes.

Python code:
```python
class A:
    pass
a = A()
if isinstance(a,A) and type(a) is A:
    print("class typing works")   
b = 5.5
if isinstance(b,float):  # or int, since both convert to number in lua
    print("number typing works")
c = "my string"
if isinstance(c,str):
    print("string typing works")
d = []
if type(d) is list and isinstance(d,list):
    print("list type works")
e = {}
if type(e) is dict and isinstance(e,dict):
    print("dict type works")
if type(d) is dict or type(e) is list:
    print("not good")
    
```

Lua code:
```lua
local A = class(function(A)
    return A
end, "A", {}, {}, {})
local a = A()
if (isinstance(a, A) and (type(a) == A)) then
    print("class typing works")
end
local b = 5.5
if isinstance(b, float) then
    print("number typing works")
end
local c = "my string"
if isinstance(c, str) then
    print("string typing works")
end
local d = list {}
if ((type(d) == list) and isinstance(d, list)) then
    print("list type works")
end
local e = dict {}
if ((type(e) == dict) and isinstance(e, dict)) then
    print("dict type works")
end
if ((type(d) == dict) or (type(e) == list)) then
    print("not good")
end
```

Output:
class typing works  
number typing works  
string typing works  
list type works  
dict type works  

### Try/Except block

Python code:
```python
try:
    print('test')
    xpcall()
    print('still going')
except:
    print('Error in function')
print('running')
```
Lua code
```lua
local ret, err = xpcall(function()
    print("test")
    xpcall()
    print("still going")
end, function(Error)
    print("Error in function")
end)
print("running")
```
Output:

test  
Error in function  
running  