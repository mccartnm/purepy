purepy
======
Pure virtual class functionality in Python.

A _very_ small metaclass to do some of the testing for us.

## The What
In C++ and other strong typed, OOP, languages, we use virtual classes and pure virtual classes to help
handle some incredibly cool paradigms when it comes to plugin design, object organization and more.

Python thinks of _everything_ as a virtual class. Which is great because polymorphism doesn't
require us to explicity set which functions are virtual or overloaded.

## The Why
So, with this knowledge, you ask, "Why bother with pure virtual classes? There are plently of reasons
not to use this in Python." You would be right! There's plenty of reasons _not_ to use/need this tool.

But, when the need arrises, you may just find this quite helpful. For us, we found it most useful when
we were integrating an API into multiple third party applications and wanted to assure ourselves we had
the right functionality and signatures without needing to write additional test code or wait for the
interpreter to make an instance of an ABCMeta object for it to fail.

## The Advantage
We first took a stab with the `abc.ABCMeta` object from Pythons default libs but ran into the issue of
"I can do whatever I want and until the object is made, it can be wrong!". Which is killer, because it
allows for crazy stuff like `setattr()` and dynamic class building _but_, when it comes to integration
of an app, there's usually less desire for out-there solutions like `__setitem__` or `setattr()`.

We want the interpreter, as soon as it loads our class into memory, to alert us if it's not "up to
code" and tell us what we need to fix about it. This is very "preprocessor" like and it has some major
advantages and a few caveats.

## Basic Example

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
# - 'Overload': The following pure virtual functions must be overloaded from base: 'Interface' before class can be used:
#     - def load(self, filepath=None)
```
