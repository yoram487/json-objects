__author__ = 'Yoram_Abenhaim'

from jsonobjects import JsonObjectDecoder
import json
    
    
class AClass:
    def __init__(self,*args,**kwargs):
        self.args=args
        self.kwargs=kwargs
        
    def __str__(self):
        return "<AClass %s, %s>"%(
            ",".join(["%s"%a for a in self.args]),
            ",".join(["%s=%s"%a for a in self.kwargs.iteritems()])            
        )

def AMethod(*args,**kwargs):
    return "I was returned by AMethod"


class noFaultJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return str(obj)
    

if __name__ == '__main__':
    
    JsonObjectDecoder.learnObj(AClass,AMethod)
   
    
    test_json_string="""
    {
        "ClassObject_1": AClass(55,msg="We will create a AClass"),
        "MethodResult_q": AMethod(),
        "ANonymous": UnknowClassYet(msg="Hello"),
        "BuiltiN": dict(a="a",b="b"),
        "LikeUsual":{"55":55}
    }
    """
    
    res = json.loads(test_json_string,cls = JsonObjectDecoder)
    
    print json.dumps(res,indent=2,cls=noFaultJSONEncoder)
    #Prints out     
    #{
    #   "LikeUsual": {
    #     "55": 55
    #   },
    #   "MethodResult_q": "I was returned by AMethod",
    #   "ClassObject_1": "<AClass 55, msg=We will create a AClass",
    #   "BuiltiN": {
    #     "a": "a",
    #     "b": "b"
    #   },
    #   "ANonymous": "UnknowClassYet(msg=\"Hello\")"
    # }
    
    import collections
    res["ANonymous"].name = "OrderedDict"
    print res["ANonymous"](collections)
    #Prints
    #OrderedDict([('msg', u'Hello')])
    
    #You can even reuse it
    import sys
    current_module = sys.modules[__name__]
    res["ANonymous"].name = "AClass"
    print res["ANonymous"](current_module)
    
    #Prints
    #<AClass , msg=Hello>
     
    #You can ask it to ignore some builtin functions names .. here dict will be thought of as a Anonymous
    res = json.loads(test_json_string,cls=JsonObjectDecoder,skip_resolve_fnames=["dict"])
    
    print json.dumps(res,indent=2,cls=noFaultJSONEncoder)
    #Prints : 
    #     {
    #   "LikeUsual": {
    #     "55": 55
    #   },
    #   "MethodResult_q": "I was returned by AMethod",
    #   "ClassObject_1": "<AClass 55, msg=We will create a AClass>",
    #   "BuiltiN": "dict(a=\"a\",b=\"b\")",
    #   "ANonymous": "UnknowClassYet(msg=\"Hello\")"
    # }
    
    #Note dict is now an Anonymous so we can do this
    res["BuiltiN"].name = "OrderedDict"
    print res["BuiltiN"](collections)
    
    #Prints
    #OrderedDict([('a', u'a'), ('b', u'b')])
    
    
    
    
    
