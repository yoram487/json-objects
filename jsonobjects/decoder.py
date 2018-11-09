__author__ = 'Yoram_Abenhaim'

import json
import re
import itertools
from operator import *
from collections import *

class AnonymousClass:
    def __init__(self,name,args,kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
    def __call__(self, from_module):
        return getattr(from_module,self.name)(*self.args,**self.kwargs)
    def __str__(self):
        return self.__unicode__()
    def asJsonEncodable(self):
        return self.__unicode__()
    def __unicode__(self):
        getprint= lambda v:'"%s"'%v if isinstance(v,unicode) else "%s"%v
        res = self.name+"("
        if self.args:
            res += ",".join([getprint(v) for v in self.args])
        if self.kwargs:
            if self.args:
                res += ","
            res += ",".join(["%s=%s"%(v[0],getprint(v[1])) for v in self.kwargs.iteritems()])
        res += ")"
        return res

NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL))


def custom_make_scanner(context):
    KNOWN_OBJECTS = context.KNOWN_OBJECTS
    skip_resolve_fnames = context.skip_resolve_fnames
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    encoding = context.encoding
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    def _scan_once(string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration

        if nextchar == '"':
            return parse_string(string, idx + 1, encoding, strict)
        elif nextchar == '{':
            return parse_object((string, idx + 1), encoding, strict,
                _scan_once, object_hook, object_pairs_hook)
        elif nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        elif nextchar == 'n' and string[idx:idx + 4] == 'null':
            return None, idx + 4
        elif nextchar == 'N' and string[idx:idx + 4] == 'None':
            return None, idx + 4
        elif nextchar == 't' and string[idx:idx + 4] == 'true':
            return True, idx + 4
        elif nextchar == 'f' and string[idx:idx + 5] == 'false':
            return False, idx + 5
        elif nextchar == 'T' and string[idx:idx + 4] == 'True':
            return True, idx + 4
        elif nextchar == 'F' and string[idx:idx + 5] == 'False':
            return False, idx + 5
        m = match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            return res, m.end()
        elif nextchar == 'N' and string[idx:idx + 3] == 'NaN':
            return parse_constant('NaN'), idx + 3
        elif nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
            return parse_constant('Infinity'), idx + 8
        elif nextchar == '-' and string[idx:idx + 9] == '-Infinity':
            return parse_constant('-Infinity'), idx + 9
        else:
            bracket_idx = string[idx:].find('(')
            equal_idx = string[idx:].find('=')
            if bracket_idx == -1 and equal_idx == -1:
                raise StopIteration
            if equal_idx != -1 and (equal_idx < bracket_idx or bracket_idx == -1) :
                k,d,v = string[idx:].partition("=")
                k=k.strip()
                nexti = sum( 1 for _ in itertools.takewhile(str.isspace,v))
                nv,nc=_scan_once(v,nexti)
                nexti = idx+nc+equal_idx+1
                nexti += sum( 1 for _ in itertools.takewhile(str.isspace,string[nexti:]))
                return {k:nv},nexti
            object_name = string[idx:idx+bracket_idx]
            object_args = []
            object_kwargs = {}
            cursor_idx = idx+bracket_idx+1
            bracket_counter = 1
            while(bracket_counter):
                if string[cursor_idx] == "(":
                    bracket_counter += 1
                    cursor_idx +=1
                elif string[cursor_idx] == ")":
                    bracket_counter -= 1
                    cursor_idx +=1
                else:
                    next_arg,cursor_idx = _scan_once(string,cursor_idx)
                    if isinstance(next_arg,dict):
                        object_kwargs.update(next_arg)
                    else:
                        object_args.append(next_arg)
                    if string[cursor_idx]==",":
                        cursor_idx += 1
            if object_name not in skip_resolve_fnames:
                if object_name in globals()['__builtins__']:
                    Obj = globals()['__builtins__'][object_name]
                elif object_name in globals():
                    Obj = globals()[object_name]
                elif object_name in KNOWN_OBJECTS:
                    Obj = KNOWN_OBJECTS[object_name]
                else:
                    return AnonymousClass(object_name,object_args,object_kwargs),cursor_idx
            else:
                res = AnonymousClass(object_name,object_args,object_kwargs),cursor_idx
                return res
                
            return Obj(*object_args,**object_kwargs),cursor_idx
    return _scan_once

class JsonObjectDecoder(json.JSONDecoder):
    KNOWN_OBJECTS={}
    def __init__(self,*args,**kwargs):
        self.skip_resolve_fnames = kwargs.pop("skip_resolve_fnames",[])
        res = super(JsonObjectDecoder, self).__init__(*args,**kwargs)
        self.scan_once = custom_make_scanner(self)
        return res
    @classmethod
    def make_decodable(cls,func):
        cls.learnObj(func)
        return func
    @classmethod
    def learnObj(cls,*args):
        for obj in args:
            cls.KNOWN_OBJECTS[obj.__name__]=obj


