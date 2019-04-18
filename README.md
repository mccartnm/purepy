purepy
======
Pure virtual class functionality in Python.

A _very_ small metaclass to do some of the testing for us.

Branch | Status | Coverage
--- | --- | --
Master | [![Build Status](https://travis-ci.org/mccartnm/purepy.svg?branch=master)](https://travis-ci.org/mccartnm/purepy) | [![Code Coverage](https://codecov.io/gh/mccartnm/purepy/branch/master/graph/badge.svg)](https://codecov.io/gh/mccartnm/purepy)
Dev | [![Build Status](https://travis-ci.org/mccartnm/purepy.svg?branch=dev)](https://travis-ci.org/mccartnm/purepy) | [![Code Coverage](https://codecov.io/gh/mccartnm/purepy/branch/dev/graph/badge.svg)](https://codecov.io/gh/mccartnm/purepy)



## The What
In C++ and other strong typed, OOP, languages, we use virtual classes and pure virtual classes to help
handle some incredibly cool paradigms when it comes to plugin design, object organization and more.

Python thinks of _everything_ as a virtual class. Which is great because polymorphism doesn't
require us to explicitly set which functions are virtual or overloaded but instead just works!

This is awesome until it's not.

## The Why
So, with this knowledge, you ask, "Why bother with pure virtual classes? There are plenty of reasons
not to use this in Python." You would be right! There's plenty of reasons _not_ to use/need this tool.

But, when the need arises, you may just find this quite helpful. For us, we found it most useful when
we were integrating an API into multiple third party applications and wanted to assure ourselves we had
the right functionality and signatures without needing to write additional test code or wait for the
interpreter to make an instance of an ABCMeta object for it to fail.

## The Advantage
We first took a stab with the [`abc.ABCMeta`][2] object from Pythons default libs but ran into the issue of

> I can do whatever I want and _until_ the object is made, it will be wrong!

Which is good sometimes, because it allows for crazy stuff like `setattr()` and dynamic class building
_but_, when it comes to integration of an app, there's usually less desire for out-there solutions like
`__setitem__` or `setattr()`.

We want the interpreter, as soon as it loads our class into memory, to alert us if it's not "up to
code" and tell us what we need to fix about it. This is very "preprocessor" like and it has some major
advantages with a few caveats.

# Basic Example

Given the following:
```python
from purepy import PureVirtualMeta, pure_virtual

class Interface(metaclass=PureVirtualMeta):

    @pure_virtual
    def save(self, filepath=None):
        raise NotImplementedError()

    @pure_virtual
    def load(self, filepath=None):
        raise NotImplementedError()

class Overload(Interface):

    def save(self, filepath=None):
        print ("Saving")
```

If we put this into the interpreter, without even creating an instance of the Overload class, we
would get:

```python
# ...
# PureVirtualError: Virtual Class Declaration:
# - 'Overload': The following pure virtual functions must be overloaded from
#               base: 'Interface' before class can be used:
#     - def load(self, filepath=None)
```

We got that error without having to execute any manual code or writing a test. This may not be the way
you want to work, at which point you don't need this utility!

# Additional Features

To act like a proper pure virtual class, `PureVirtualMeta` and the default `pure_virtual` utilities are
_extremely_ strict when it comes to working with the classes. There are a wide variety of ways to augment
this however as described below.

### Signature Verification

By default `purepy` will assert that the signatures of the `pure_virtual` function match the
overloaded.

```python
class Interface(metaclass=PureVirtualMeta):

    @pure_virtual
    def save(self, filepath=None):
        raise NotImplementedError()

class Overload(Interface):

    def save(self):
        print ("Saving")

# Result:
# ...
# PureVirtualError: Virtual Class Declaration:
# - 'Overload': The following overload functions have the
#               wrong signature from base: 'Interface'
#     - def save(self): -> def save(self, filepath=None):
```

This can be disabled by setting the class variable `pv_explicit_args = False`

```python
class Interface(metaclass=PureVirtualMeta):
    pv_explicit_args = False
    # ...
```

### Base Instances

By default `purepy` will mimic the [`abc.abstractmethod`][1] and raise and error when we try to
instantiate a pure virtual class.

```python
class Interface(metaclass=PureVirtualMeta):

    @pure_virtual
    def save(self, filepath=None):
        raise NotImplementedError()

>>> Interface()
# ...
# PureVirtualError: Cannot instantiate pure virtual class
# 'Interface' with pure virtual functions: (save)
```

This can be disabled with the class variable `pv_allow_base_instance = True`

```python
class Interface(metaclass=PureVirtualMeta):
    pv_allow_base_instance = True

    @pure_virtual
    def save(self, filepath=None):
        raise NotImplementedError()

>>> print(Interface())
# <__main__.Interface object at ...>
```

### Forced NotImplementedError

By default, the `pure_virtual` decorator will force all it's functions to raise a `NotImplementedError` even
when there is information defined and the class can be instantiated.

```python
class Interface(metaclass=PureVirtualMeta):
    pv_allow_base_instance = True

    @pure_virtual
    def save(self, filepath=None):
        print ("Saving ", str(filepath))
>>> inst = Interface()
>>> inst.save("foo")
# ...
# NotImplementedError: Illegal call to pure virtual function save
```

This can be disabled with a custom decorator by setting `force_not_implemented = False`.

```python
my_pure_virtual = PureVirtualMeta.new(force_not_implemented=False)

class Interface(metaclass=PureVirtualMeta):
    pv_allow_base_instance = True

    @my_pure_virtual
    def save(self, filepath=None):
        print ("Saving ", filepath)
>>> inst = Interface()
>>> inst.save("foo")
# Saving foo
```

# Customized Decorator

By default, the `pure_virtual` decorator provided is quite strict. In some cases you may want to
augment the properties to make it more forgiving. This can be done with the `PureVirtualMeta.new()`
and `PureVirtualMeta.new_class()` functions. Both functions take additional `**kwargs` that augment the
decorator and subsequent validation.

```python
my_pure_virtual = PureVirtualMeta.new(strict_types=False)

class Interface(metaclass=PureVirtualMeta):

    @my_pure_virtual
    def foo(self, filepath: str):
        raise NotImplementedError()

class Overload(Interface):

    # This is NOT okay by default, but okay with our custom decorator 
    def foo(self, filepath):
        pass
```

# Registry
There are two ways to control/retrieve the pure virtual functions available in the api.

## From Id
Each `pure_virtual` decorator gets a unique identifier and all functions it its registry are handled
underneath that.

```python
class Interface(metaclass=PureVirtualMeta):

    @pure_virtual
    def foo(self, filepath):
        raise NotImplementedError()

print (PureVirtualMeta.virtual_functions_from_id(pure_virtual.id()))
# [<function Interface.save at ...>]
```

## From Class
Each class registers the pure virtual functions and can be polled by both the class and an instance of
said class.

```python
class Interface(metaclass=PureVirtualMeta):

    pv_allow_base_instance = True

    @pure_virtual
    def foo(self, filepath):
        raise NotImplementedError()

print (PureVirtualMeta.pure_virtual_functions(Interface))
# [<function Interface.save at ...>]
print (PureVirtualMeta.pure_virtual_functions(Interface()))
# [<function Interface.save at ...>]
print (PureVirtualMeta.is_pure_virtual_class(Interface))
# True
```

[1]:(https://docs.python.org/3/library/abc.html#abc.abstractmethod)
[2]:(https://docs.python.org/3/library/abc.html)