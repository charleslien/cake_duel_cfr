#!/usr/bin/python3

import enum

class StrValueEnum(enum.IntEnum):
  def __str__(self):
    return self.value

def countDictToList(count_dict):
  ret = []
  for key in count_dict:
    ret += [key] * count_dict[key]

  return ret

def listToCountDict(lst):
  ret = {}
  for val in lst:
    ret[val] = ret.get(val, 0) + 1
  
  return ret
