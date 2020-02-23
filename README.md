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

<details><summary>For example</summary>
<p>

```lua
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
</details>

## Features



### Attributes
<details><summary>Open</summary>
<p>
Python code:

```python
foo.bar.baz.one.two.three("Hello, world!")
```
</p>
<p>
Lua code:

```lua
foo.bar.baz.one.two.three("Hello, world!")
```
</p>
<p>
Output:


</p>
</details>

### Class
<details><summary>Open</summary>
<p>
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
</p>
<p>
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
end, "Animal", {}, {}, {})
local Dog = class(function(Dog)
    function Dog.say_hello(self)
        print((("Hello, my name is: " + self.name) + "!"))
        self.bark()
    end
    function Dog.bark(self)
        print("Bark! Bark! Bark!")
    end
    return Dog
end, "Dog", {Animal}, {}, {})
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
</p>
<p>
Output:

Hello, my name is: Sparky!
Hello, my name is: Barky!
Bark! Bark! Bark!
Bark! Bark! Bark!
Animal.PLANET = 	Earth
sparky.PLANET = 	Earth
barky.PLANET = 	Earth
Animal.PLANET = 	Mars
sparky.PLANET = 	Mars

</p>
</details>

### Class_Extended
<details><summary>Open</summary>
<p>
Python code:

```python
class example:
    def __init__(self, v):
        self.value = v

    def __add__(self, other):
        return example(self.value+other.value)

    def __sub__(self, other):
        return example(self.value-other.value)

    def __mul__(self, other):
        return example(self.value*other.value)

    def __truediv__(self, other):
        return example(self.value/other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        return str(self.value)

    @property
    def prop(self):
        return self.value

    @prop.setter
    def prop(self,new):
        if new > 5:
            self.value = new


a = example(5)
b = example(6)
print(a+b)
print(a-b)
print(a*b)
print(a/b)
print(a.prop)
a.prop = 4
print(a.prop)
a.prop = 6
print(a.prop)

```
</p>
<p>
Lua code:

```lua
local example = class(function(example)
    function example.__init__(self, v)
        self.value = v
    end
    function example.__add__(self, other)
        return example((self.value + other.value))
    end
    function example.__sub__(self, other)
        return example((self.value - other.value))
    end
    function example.__mul__(self, other)
        return example((self.value * other.value))
    end
    function example.__truediv__(self, other)
        return example((self.value / other.value))
    end
    function example.__lt__(self, other)
        return (self.value < other.value)
    end
    function example.__str__(self)
        return str(self.value)
    end
    example.prop = property(function(self)
        return self.value
    end)
    example.prop = example.prop.setter(function(self, new)
        if (new > 5) then
            self.value = new
        end
    end)
    return example
end, "example", {}, {__add = "__add__", __sub = "__sub__", __mul = "__mul__", __div = "__truediv__", __lt = "__lt__", __tostring = "__str__"}, {prop = "example.prop"})
local a = example(5)
local b = example(6)
print((a + b))
print((a - b))
print((a * b))
print((a / b))
print(a.prop)
a.prop = 4
print(a.prop)
a.prop = 6
print(a.prop)
```
</p>
<p>
Output:

11
-1
30
0.83333333333333
5
5
6

</p>
</details>

### Comments
<details><summary>Open</summary>
<p>
Python code:

```python
"""Documentation comments test"""

class Animal:
    """Class-level docstring"""
    pass

def foo():
    """Function-level docstring"""
    pass

name = "John " + "Parrish"

print(name)
print("Hello!")

```
</p>
<p>
Lua code:

```lua
--[[ Documentation comments test ]]
local Animal = class(function(Animal)
    --[[ Class-level docstring ]]
    return Animal
end, "Animal", {}, {}, {})
local function foo()
    --[[ Function-level docstring ]]
end
local name = ("John " + "Parrish")
print(name)
print("Hello!")
```
</p>
<p>
Output:

John Parrish
Hello!

</p>
</details>

### Comprehensions
<details><summary>Open</summary>
<p>
Python code:

```python

a = [i * j for i in range(5) for j in range(3) if i * j % 2 == 0 and i > 0 and j > 0]

for item in a:
    print(item)

lst = ["a","b","c","d","e"]
b = {lst[i]: i ** 2 for i in range(5)}

for k in lst:
    print(k,b[k])
```
</p>
<p>
Lua code:

```lua
local a = (function() local result = list {} for i in range(5) do for j in range(3) do if (((math.fmod((i * j), 2)) == 0) and (i > 0) and (j > 0)) then result.append((i * j)) end end end return result end)()
for item in a do
    print(item)
    ::loop_label_1::
end
local lst = list {"a", "b", "c", "d", "e"}
local b = (function() local result = dict {} for i in range(5) do result[lst[i]] = (math.pow(i, 2)) end return result end)()
for k in lst do
    print(k, b[k])
    ::loop_label_2::
end
```
</p>
<p>
Output:

2
2
4
6
4
8
a	0.0
b	1.0
c	4.0
d	9.0
e	16.0

</p>
</details>

### Continue
<details><summary>Open</summary>
<p>
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
</p>
<p>
Lua code:

```lua
for i in range(10) do
    if (i == 5) then
        goto loop_label_3
    end
    for j in range(10) do
        if (j == 7) then
            goto loop_label_4
        end
        print(i, " * ", j, " = ", (i * j))
        ::loop_label_4::
    end
    ::loop_label_3::
end
```
</p>
<p>
Output:

0	 * 	0	 = 	0
0	 * 	1	 = 	0
0	 * 	2	 = 	0
0	 * 	3	 = 	0
0	 * 	4	 = 	0
0	 * 	5	 = 	0
0	 * 	6	 = 	0
0	 * 	8	 = 	0
0	 * 	9	 = 	0
1	 * 	0	 = 	0
1	 * 	1	 = 	1
1	 * 	2	 = 	2
1	 * 	3	 = 	3
1	 * 	4	 = 	4
1	 * 	5	 = 	5
1	 * 	6	 = 	6
1	 * 	8	 = 	8
1	 * 	9	 = 	9
2	 * 	0	 = 	0
2	 * 	1	 = 	2
2	 * 	2	 = 	4
2	 * 	3	 = 	6
2	 * 	4	 = 	8
2	 * 	5	 = 	10
2	 * 	6	 = 	12
2	 * 	8	 = 	16
2	 * 	9	 = 	18
3	 * 	0	 = 	0
3	 * 	1	 = 	3
3	 * 	2	 = 	6
3	 * 	3	 = 	9
3	 * 	4	 = 	12
3	 * 	5	 = 	15
3	 * 	6	 = 	18
3	 * 	8	 = 	24
3	 * 	9	 = 	27
4	 * 	0	 = 	0
4	 * 	1	 = 	4
4	 * 	2	 = 	8
4	 * 	3	 = 	12
4	 * 	4	 = 	16
4	 * 	5	 = 	20
4	 * 	6	 = 	24
4	 * 	8	 = 	32
4	 * 	9	 = 	36
6	 * 	0	 = 	0
6	 * 	1	 = 	6
6	 * 	2	 = 	12
6	 * 	3	 = 	18
6	 * 	4	 = 	24
6	 * 	5	 = 	30
6	 * 	6	 = 	36
6	 * 	8	 = 	48
6	 * 	9	 = 	54
7	 * 	0	 = 	0
7	 * 	1	 = 	7
7	 * 	2	 = 	14
7	 * 	3	 = 	21
7	 * 	4	 = 	28
7	 * 	5	 = 	35
7	 * 	6	 = 	42
7	 * 	8	 = 	56
7	 * 	9	 = 	63
8	 * 	0	 = 	0
8	 * 	1	 = 	8
8	 * 	2	 = 	16
8	 * 	3	 = 	24
8	 * 	4	 = 	32
8	 * 	5	 = 	40
8	 * 	6	 = 	48
8	 * 	8	 = 	64
8	 * 	9	 = 	72
9	 * 	0	 = 	0
9	 * 	1	 = 	9
9	 * 	2	 = 	18
9	 * 	3	 = 	27
9	 * 	4	 = 	36
9	 * 	5	 = 	45
9	 * 	6	 = 	54
9	 * 	8	 = 	72
9	 * 	9	 = 	81

</p>
</details>

### Decorator
<details><summary>Open</summary>
<p>
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
</p>
<p>
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
local hello = italic(strong(function(name)
    return (("Hello, " + name) + "!")
end))
print(hello("John"))
```
</p>
<p>
Output:

<em><strong>Hello, John!</strong></em>

</p>
</details>

### Defaultargs
<details><summary>Open</summary>
<p>
Python code:

```python
def hello(name, age=20, nickname="", *args):
    print("Hello, my name is " + name + " and I'm " + str(age))
    print("My nickname is " + nickname)

hello("John", 12, "antikiller")
hello("Josh", 45)
hello("Jane")

```
</p>
<p>
Lua code:

```lua
local function hello(name, age, nickname, ...)
    age = age or 20
    nickname = nickname or ""
    local args = list {...}
    print(((("Hello, my name is " + name) + " and I'm ") + str(age)))
    print(("My nickname is " + nickname))
end
hello("John", 12, "antikiller")
hello("Josh", 45)
hello("Jane")
```
</p>
<p>
Output:

Hello, my name is John and I'm 12
My nickname is antikiller
Hello, my name is Josh and I'm 45
My nickname is 
Hello, my name is Jane and I'm 20
My nickname is 

</p>
</details>

### Del
<details><summary>Open</summary>
<p>
Python code:

```python
a, b, c = 1, 2, 3
print(a, b, c)
del a, b
print(a, b, c)
del c
print(a, b, c)
```
</p>
<p>
Lua code:

```lua
local a, b, c = 1, 2, 3
print(a, b, c)
a, b = nil, nil
print(a, b, c)
c = nil
print(a, b, c)
```
</p>
<p>
Output:

1	2	3
nil	nil	3
nil	nil	nil

</p>
</details>

### Factorial
<details><summary>Open</summary>
<p>
Python code:

```python
def factorial(value):
    return 1 if value == 0 else value * factorial(value - 1)

print(factorial(5))
print(factorial(10))
print(factorial(3))
print(factorial(0))

```
</p>
<p>
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
</p>
<p>
Output:

120
3628800
6
1

</p>
</details>

### For
<details><summary>Open</summary>
<p>
Python code:

```python
for i in range(10):
    print(i)

k = [1, 2, 3]
print(len(k))
```
</p>
<p>
Lua code:

```lua
for i in range(10) do
    print(i)
    ::loop_label_5::
end
local k = list {1, 2, 3}
print(len(k))
```
</p>
<p>
Output:

0
1
2
3
4
5
6
7
8
9
3

</p>
</details>

### Global
<details><summary>Open</summary>
<p>
Python code:

```python
foo = 42

def bar():
    global foo
    foo = 34

print("foo = ", foo)
bar()
print("foo = ", foo)
```
</p>
<p>
Lua code:

```lua
local foo = 42
local function bar()
    foo = 34
end
print("foo = ", foo)
bar()
print("foo = ", foo)
```
</p>
<p>
Output:

foo = 	42
foo = 	34

</p>
</details>

### Ifelse
<details><summary>Open</summary>
<p>
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
```
</p>
<p>
Lua code:

```lua
local a = 45
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
```
</p>
<p>
Output:

a > 5
a >= 45
a == 45
50 < x < 150

</p>
</details>

### Import
<details><summary>Open</summary>
<p>
Python code:

```python
import foo.bar
import bar as bar_ex
```
</p>
<p>
Lua code:

```lua
local bar = require("foo.bar")
local bar_ex = require("bar")
```
</p>
<p>
Output:


</p>
</details>

### In
<details><summary>Open</summary>
<p>
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
</p>
<p>
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
</p>
<p>
Output:

2 < 3
true
true
false
true
false
true
true
false
true

</p>
</details>

### Iterdict
<details><summary>Open</summary>
<p>
Python code:

```python
book = {
    "title": "Harry Potter and the philosopher's stone",
    "author": "J. K. Rowling",
    "year": 1997,
}

k = 0
for i in book:
    k += 1
    if k > 1:
        break

for i in book:
    pass

```
</p>
<p>
Lua code:

```lua
local book = dict {["title"] = "Harry Potter and the philosopher's stone", ["author"] = "J. K. Rowling", ["year"] = 1997}
local k = 0
for i in book do
    k = (k + 1)
    if (k > 1) then
        break
    end
    ::loop_label_6::
end
for i in book do
    ::loop_label_7::
end
```
</p>
<p>
Output:


</p>
</details>

### Iterlist
<details><summary>Open</summary>
<p>
Python code:

```python
a = [1, 4, 8, 16, 52, 34, 78, 342]

k = 0

strange_sum = 0
for i in a:
    k += 1
    if k > 3:
        break

    print("Current i is: ", i)
    strange_sum += i

print("After break: ")

for i in a:
    print("Current i is: ", i)
    strange_sum += i

print("Some strange sum is: ", strange_sum)
```
</p>
<p>
Lua code:

```lua
local a = list {1, 4, 8, 16, 52, 34, 78, 342}
local k = 0
local strange_sum = 0
for i in a do
    k = (k + 1)
    if (k > 3) then
        break
    end
    print("Current i is: ", i)
    strange_sum = (strange_sum + i)
    ::loop_label_8::
end
print("After break: ")
for i in a do
    print("Current i is: ", i)
    strange_sum = (strange_sum + i)
    ::loop_label_9::
end
print("Some strange sum is: ", strange_sum)
```
</p>
<p>
Output:

Current i is: 	1
Current i is: 	4
Current i is: 	8
After break: 
Current i is: 	1
Current i is: 	4
Current i is: 	8
Current i is: 	16
Current i is: 	52
Current i is: 	34
Current i is: 	78
Current i is: 	342
Some strange sum is: 	548

</p>
</details>

### Lambda
<details><summary>Open</summary>
<p>
Python code:

```python
sqr = lambda x: x * x
print(sqr(2))
print(sqr(8))
```
</p>
<p>
Lua code:

```lua
local sqr = function(x) return (x * x) end
print(sqr(2))
print(sqr(8))
```
</p>
<p>
Output:

4
64

</p>
</details>

### Listdict
<details><summary>Open</summary>
<p>
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

print(a[1])
print(b[0][1])
print(c["firstname"], c["lastname"])

ch = c["children"][0]
print(ch["name"], ch["age"])
```
</p>
<p>
Lua code:

```lua
local a = list {1, 2, 5}
local b = list {list {1, 2, 3}, list {4, 5, 6}, list {7, 8, 9}}
local c = dict {["firstname"] = "John", ["lastname"] = "Doe", ["age"] = 42, ["children"] = list {dict {["name"] = "Sara", ["age"] = 4}}}
print(a[1])
print(b[0][1])
print(c["firstname"], c["lastname"])
local ch = c["children"][0]
print(ch["name"], ch["age"])
```
</p>
<p>
Output:

2
2
John	Doe
Sara	4

</p>
</details>

### Localvars
<details><summary>Open</summary>
<p>
Python code:

```python
i = 10
j = 5
while i > 0:
    print(i)
    i = i - 1
    test = 3434

test = 56

def fact(n):
    return 1 if n == 0 else n * fact(n - 1)

class Foo:
    def __init__(self):
        self.cls_var = 45
        localvar = 56
```
</p>
<p>
Lua code:

```lua
local i = 10
local j = 5
while (i > 0) do
    print(i)
    i = (i - 1)
    local test = 3434
    ::loop_label_10::
end
local test = 56
local function fact(n)
    return (n == 0) and 1 or (n * fact((n - 1)))
end
local Foo = class(function(Foo)
    function Foo.__init__(self)
        self.cls_var = 45
        local localvar = 56
    end
    return Foo
end, "Foo", {}, {}, {})
```
</p>
<p>
Output:

10
9
8
7
6
5
4
3
2
1

</p>
</details>

### Luacode
<details><summary>Open</summary>
<p>
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
</p>
<p>
Lua code:

```lua
local function get_summ(a, b)
    return (a + b)
end
print(get_summ(3, 5))

local c = 45
print(c)

```
</p>
<p>
Output:

8
45

</p>
</details>

### Nestedclass
<details><summary>Open</summary>
<p>
Python code:

```python
class Foo:
    class Bar:
        def __init__(self):
            print("__init__ from Bar")
    
    def __init__(self):
        print("__init__ from Foo")
        Foo.Bar()

Foo()
Foo.Bar()
```
</p>
<p>
Lua code:

```lua
local Foo = class(function(Foo)
    Foo.Bar = class(function(Bar)
        function Bar.__init__(self)
            print("__init__ from Bar")
        end
        return Bar
    end, "Bar", {}, {}, {})
    function Foo.__init__(self)
        print("__init__ from Foo")
        Foo.Bar()
    end
    return Foo
end, "Foo", {}, {}, {})
Foo()
Foo.Bar()
```
</p>
<p>
Output:

__init__ from Foo
__init__ from Bar
__init__ from Bar

</p>
</details>

### Simple_Math
<details><summary>Open</summary>
<p>
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
</p>
<p>
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
</p>
<p>
Output:

8
16
25
32.0
121.0
5
5.5
172.18867924528

</p>
</details>

### Try
<details><summary>Open</summary>
<p>
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
</p>
<p>
Lua code:

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
</p>
<p>
Output:

test
Error in function
running

</p>
</details>

### Type
<details><summary>Open</summary>
<p>
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
</p>
<p>
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
</p>
<p>
Output:

class typing works
number typing works
string typing works
list type works
dict type works

</p>
</details>

### Unaryop
<details><summary>Open</summary>
<p>
Python code:

```python
a = 45
a = -a

b = +a

c = ~a

test = True
nt = not test

print(a, b, c)
print(test, nt)
```
</p>
<p>
Lua code:

```lua
local a = 45
a = -a
local b = a
local c = bit32.bnot(a)
local test = true
local nt = not test
print(a, b, c)
print(test, nt)
```
</p>
<p>
Output:

-45	-45	44
true	false

</p>
</details>

### Varargs
<details><summary>Open</summary>
<p>
Python code:

```python
def foo():
    pass

def varargs(name, *args):
    print("Name is: ", name)
    print(*args)

varargs("first", 1, 3, 6, 4, 7)
varargs("second", "hello", "python", "world")
```
</p>
<p>
Lua code:

```lua
local function foo()

end
local function varargs(name, ...)
    local args = list {...}
    print("Name is: ", name)
    print(unpack(args))
end
varargs("first", 1, 3, 6, 4, 7)
varargs("second", "hello", "python", "world")
```
</p>
<p>
Output:

Name is: 	first
1	3	6	4	7
Name is: 	second
hello	python	world

</p>
</details>

### Variables
<details><summary>Open</summary>
<p>
Python code:

```python
a = 45
b = 100

a, b = b, a

c = a * b
d = c / (1 + 1)

print(a)
print(b)
print(c)
print(d)
```
</p>
<p>
Lua code:

```lua
local a = 45
local b = 100
local a, b = b, a
local c = (a * b)
local d = (c / (1 + 1))
print(a)
print(b)
print(c)
print(d)
```
</p>
<p>
Output:

100
45
4500
2250.0

</p>
</details>

### While
<details><summary>Open</summary>
<p>
Python code:

```python
i = 10
while i > 0:
    print(i)
    i -= 1
```
</p>
<p>
Lua code:

```lua
local i = 10
while (i > 0) do
    print(i)
    i = (i - 1)
    ::loop_label_11::
end
```
</p>
<p>
Output:

10
9
8
7
6
5
4
3
2
1

</p>
</details>

### With
<details><summary>Open</summary>
<p>
Python code:

```python
with open("output") as output_file:
    output_file.write(input_file.read())

```
</p>
<p>
Lua code:

```lua
do
    local output_file = open("output")
    output_file.write(input_file.read())
end
```
</p>
<p>
Output:


</p>
</details>
