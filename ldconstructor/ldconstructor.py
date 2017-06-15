import logging
from pprint import pformat

def construct(**args):
    return StructureBuilder(attr_dict=args)
def startFrom(root, **args):
    return StructureBuilder(root=root, attr_dict=args)
def follow(pred, **args):
    return StructureBuilder(pred=pred, attr_dict=args, mincard=1)
def optfollow(pred, **args):
    return StructureBuilder(pred=pred, attr_dict=args)

class Thing():
    """
    Base class for all classes dynamically created from StructureBuilder
    """
    def __str__(self):
        obj = {}
        for k in self._keys:
            obj[k] = self.__getattribute__(k)
        return pformat(obj)
    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        obj = {}
        for k in self._keys:
            v = self.__getattribute__(k)
            if v is not None:
                if 'to_json' in v:
                    v = v.to_json()
                else:
                    v = str(v)
                obj[k] = v
        return obj
        

class StructureBuilder():
    """
    Represents the structure of a hierarchical object which is filled in by a series of queries
    to a triplestore
    """
    def __init__(self, root=None, pred=None, attr_dict={}, mincard=0, recursedepth=1):
        self.type = None
        self.root = root
        self.pred = pred
        self.attr_dict = attr_dict

    def make(self, root=None, stack=[]):
        """
        fillout the structure by iterative querying
        """
        print('Stack={}'.format(stack))
        # python type
        cls_name = self.type
        if root is None:
            root = self.root
        else:
            if self.root is not None:
                logging.error("Hmm root = {} and {}, pred={} in {}".format(root, self.root, self.pred, self.attr_dict))
                raise ValueException()
            
        newobj_dict = {}
        for k,v in self.attr_dict.items():
            if k == '_type':
                cls_name = v
            else:
                vals = []
                if isinstance(v, StructureBuilder):
                    if v.root is not None:
                        vals = [v.make(stack=stack+['x'])]
                    else:
                        objs = self.triple(root, v.pred)
                        for obj in objs:
                            next_v = v.make(root=obj, stack=stack+[obj])
                            vals.append(next_v)
                else:
                    vals = [v]
                newobj_dict[k] = vals

        newobj_dict['id'] = root
        newobj_dict['_keys'] = list(newobj_dict.keys())
        if cls_name is None:
            cls_name = 'HELLO'
        cls = type(cls_name,(Thing,),newobj_dict)
        newobj = cls()
        for k,v in newobj_dict.items():
            newobj.__setattr__(k,v)
        return newobj
        
    def triple(self, subj, pred):
        if subj is None:
            raise ValueException()
        return ['{}-{}-1'.format(subj,pred),'x2']

class Crawler:
    """
    Abstract superclass of all data crawlers
    """
    pass

class RdflibCrawler(Crawler):
    def __init__(self,graph=None):
        self.graph = graph
    def crawl(self, subj, pred):
        return [o for (s,p,o) in self.graph.triples((subj,pred,None))]


class EndpointCrawler(Crawler):
    """
    Crawler that uses a REST service or other HTTP endpoint
    """
    pass

class SparqlCrawler(EndpointCrawler):
    pass

class NeoBoltCrawler(EndpointCrawler):
    pass

# test

enabled_by = 'ro1'
occurs_in = 'ro2'
part_of = 'BFO:0000050'

g1='g1'
g2='g2'
sb = construct(left=startFrom(g1,
                              enabled_by=follow(enabled_by,
                                                type='a',
                                                occurs_in=optfollow(occurs_in,
                                                                    part_of=optfollow(part_of)))),
               right=startFrom(g2,
                              enabled_by=follow(enabled_by,
                                                type='a',
                                                occurs_in=optfollow(occurs_in,
                                                                    part_of=optfollow(part_of)))),
               _type='Interaction')
obj = sb.make()
print(str(obj))
import json
print(str(json.dumps(obj.to_dict(),
                 sort_keys=True,
                 indent=4, separators=(',', ': '))))
