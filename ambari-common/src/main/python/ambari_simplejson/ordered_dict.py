#!/usr/bin/env python3
"""Drop-in replacement for collections.OrderedDict by Raymond Hettinger

http://code.activestate.com/recipes/576693/

"""

from UserDict import DictMixin


class OrderedDict(dict, DictMixin):
  def __init__(self, *args, **kwds):
    if len(args) > 1:
      raise TypeError(f"expected at most 1 arguments, got {len(args)}")
    try:
      self.__end
    except AttributeError:
      self.clear()
    self.update(*args, **kwds)

  def clear(self):
    self.__end = end = []
    end += [None, end, end]  # sentinel node for doubly linked list
    self.__map = {}  # key --> [key, prev, next]
    dict.clear(self)

  def __setitem__(self, key, value):
    if key not in self:
      end = self.__end
      curr = end[1]
      curr[2] = end[1] = self.__map[key] = [key, curr, end]
    dict.__setitem__(self, key, value)

  def __delitem__(self, key):
    dict.__delitem__(self, key)
    key, prev, next = self.__map.pop(key)
    prev[2] = next
    next[1] = prev

  def __iter__(self):
    end = self.__end
    curr = end[2]
    while curr is not end:
      yield curr[0]
      curr = curr[2]

  def __reversed__(self):
    end = self.__end
    curr = end[1]
    while curr is not end:
      yield curr[0]
      curr = curr[1]

  def popitem(self, last=True):
    if not self:
      raise KeyError("dictionary is empty")
    key = next(reversed(self)) if last else next(iter(self))
    value = self.pop(key)
    return key, value

  def __reduce__(self):
    items = [[k, self[k]] for k in self]
    tmp = self.__map, self.__end
    del self.__map, self.__end
    inst_dict = vars(self).copy()
    self.__map, self.__end = tmp
    if inst_dict:
      return (self.__class__, (items,), inst_dict)
    return self.__class__, (items,)

  def keys(self):
    return list(self)

  setdefault = DictMixin.setdefault
  update = DictMixin.update
  pop = DictMixin.pop
  values = DictMixin.values
  items = DictMixin.items
  iterkeys = DictMixin.iterkeys
  itervalues = DictMixin.itervalues
  iteritems = DictMixin.iteritems

  def __repr__(self):
    if not self:
      return f"{self.__class__.__name__}()"
    return f"{self.__class__.__name__}({self.items()!r})"

  def copy(self):
    return self.__class__(self)

  @classmethod
  def fromkeys(cls, iterable, value=None):
    d = cls()
    for key in iterable:
      d[key] = value
    return d

  def __eq__(self, other):
    if isinstance(other, OrderedDict):
      return len(self) == len(other) and all(
        p == q for p, q in zip(self.items(), other.items())
      )
    return dict.__eq__(self, other)

  def __ne__(self, other):
    return not self == other
