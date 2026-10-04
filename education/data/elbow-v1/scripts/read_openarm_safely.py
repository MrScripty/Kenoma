#!/usr/bin/env python3
"""Passive, deliberately narrow pickle opcode reader. Never invokes pickle.load,
imports a pickle-named module, or calls a pickle-supplied callable.
Only two symbolic numpy scalar/dtype constructs are translated to built-in numbers.
Unknown instructions, types, dtype encodings, and state fail closed.
"""
import math, pickletools, struct
from dataclasses import dataclass
@dataclass
class DType:
    kind: str
    endian: str = ''
MARK = object()
ALLOWED_GLOBALS = {('numpy','dtype'),('numpy.core.multiarray','scalar')}
def read_passive(blob):
    if len(blob) > 2_000_000: raise ValueError('Input size limit')
    stack=[]; memo={}; stopped=False
    def marked():
        i=len(stack)-1
        while i>=0 and stack[i] is not MARK: i-=1
        if i<0: raise ValueError('Missing mark')
        items=stack[i+1:]; del stack[i:]; return items
    for i,(op,arg,pos) in enumerate(pickletools.genops(blob)):
        if i>400000: raise ValueError('Opcode limit')
        n=op.name
        if n=='PROTO':
            if arg!=5: raise ValueError('Unexpected pickle protocol')
        elif n=='FRAME': pass
        elif n=='EMPTY_DICT': stack.append({})
        elif n=='EMPTY_LIST': stack.append([])
        elif n=='MARK': stack.append(MARK)
        elif n=='MEMOIZE': memo[len(memo)]=stack[-1]
        elif n in ('BINGET','LONG_BINGET'): stack.append(memo[arg])
        elif n in ('SHORT_BINUNICODE','SHORT_BINBYTES','BINFLOAT','BININT','BININT1','BININT2'): stack.append(arg)
        elif n=='NONE': stack.append(None)
        elif n=='NEWTRUE': stack.append(True)
        elif n=='NEWFALSE': stack.append(False)
        elif n=='TUPLE': stack.append(tuple(marked()))
        elif n in ('TUPLE2','TUPLE3'):
            k=int(n[-1]); items=tuple(stack[-k:]); del stack[-k:]; stack.append(items)
        elif n=='APPENDS':
            items=marked()
            if type(stack[-1]) is not list: raise ValueError('Invalid list target')
            stack[-1].extend(items)
        elif n=='APPEND':
            item=stack.pop()
            if type(stack[-1]) is not list: raise ValueError('Invalid list target')
            stack[-1].append(item)
        elif n=='SETITEMS':
            items=marked()
            if type(stack[-1]) is not dict or len(items)%2: raise ValueError('Invalid dict target')
            for j in range(0,len(items),2):
                if type(items[j]) is not str: raise ValueError('Only string keys accepted')
                stack[-1][items[j]]=items[j+1]
        elif n=='STACK_GLOBAL':
            name=stack.pop(); module=stack.pop(); pair=(module,name)
            if pair not in ALLOWED_GLOBALS: raise ValueError('Unrecognized symbolic global')
            stack.append(pair)
        elif n=='REDUCE':
            args=stack.pop(); symbolic=stack.pop()
            if symbolic==('numpy','dtype'):
                if args not in (('i4',False,True),('f8',False,True)): raise ValueError('Unexpected dtype arguments')
                stack.append(DType(args[0]))
            elif symbolic==('numpy.core.multiarray','scalar'):
                if type(args) is not tuple or len(args)!=2 or not isinstance(args[0],DType) or type(args[1]) is not bytes: raise ValueError('Unexpected scalar arguments')
                dt,b=args
                if dt.endian!='<' or dt.kind not in ('i4','f8'): raise ValueError('Unexpected scalar format')
                val=struct.unpack('<'+{'i4':'i','f8':'d'}[dt.kind],b)[0]
                if not math.isfinite(val): raise ValueError('Nonfinite scalar')
                stack.append(val)
            else: raise ValueError('Callable execution prohibited')
        elif n=='BUILD':
            state=stack.pop(); dt=stack[-1]
            if not isinstance(dt,DType) or state!=(3,'<',None,None,None,-1,-1,0): raise ValueError('Unexpected dtype state')
            dt.endian='<'
        elif n=='STOP':
            if len(stack)!=1 or type(stack[0]) is not dict or pos!=len(blob)-1: raise ValueError('Invalid final stack or trailing data')
            stopped=True; break
        else: raise ValueError('Unsupported opcode '+n)
    if not stopped: raise ValueError('No stop')
    return stack[0]
if __name__=='__main__':
    import sys,zipfile,json
    with zipfile.ZipFile(sys.argv[1]) as z: data=read_passive(z.read('time_series/2/trial_1a.p'))
    for k,v in data.items():
        print(k, type(v).__name__,len(v) if hasattr(v,'__len__') else '',str(v)[:100])
