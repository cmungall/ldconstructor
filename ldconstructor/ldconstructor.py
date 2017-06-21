import logging
from pprint import pformat
from rdflib import URIRef
from rdflib.namespace import RDF

def construct(**args):
    return StructureBuilder(attr_dict=args)
def startFrom(root, **args):
    return StructureBuilder(root=root, attr_dict=args)
def follow(pred, **args):
    return StructureBuilder(pred=pred, attr_dict=args, mincard=1)
def optfollow(pred, **args):
    return StructureBuilder(pred=pred, attr_dict=args)
def follow_rdf_type():
    return follow(RDF.type)

class Thing(object):
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
        return self._to_dict(self)
    
    def _to_dict(self,objIn):
        if isinstance(objIn,str):
            return objIn
        if isinstance(objIn,list):
            return [self._to_dict(x) for x in objIn]
        obj = {}
        for k in objIn._keys:
            v = objIn.__getattribute__(k)
            if v is not None:
                v = self._to_dict(v)
                #if isinstance(v,Thing):
                #    v = v.to_dict()
                #else:
                #    v = str(v)
                obj[k] = v
        return obj
        

class StructureBuilder():
    """
    Represents the structure of a hierarchical object which is filled in by a series of queries
    to a triplestore
    """
    def __init__(self, root=None, pred=None, attr_dict={}, mincard=0, recursedepth=1,
                 crawler=None):
        self.rdftype = None
        self.root = root
        self.pred = pred
        self.attr_dict = attr_dict
        self.crawler = crawler

    def make(self, root=None, stack=[]):
        """
        fillout the structure by iterative querying
        """
        logging.debug('Stack={}'.format(stack))
        # python type
        cls_name = self.rdftype
        if root is None:
            root = self.root
        else:
            if self.root is not None:
                logging.error("Hmm root = {} and {}, pred={} in {}".format(root, self.root, self.pred, self.attr_dict))
                raise ValueException()
            
        newobj_dict = {}
        for k,v in self.attr_dict.items():
            if k == '_type':
                logging.info("Getting cls_name from _type {}".format(v))
                cls_name = v
            else:
                vals = []
                if isinstance(v, StructureBuilder):
                    # by default, propagate crawler down.
                    # however, still possible to substitute crawlers anywhere
                    # in tree
                    if v.crawler is None:
                        v.crawler = self.crawler
                    
                    if v.root is not None:
                        vals = [v.make(stack=stack+['x'])]
                    else:
                        objs = self.crawler.crawl(root, v.pred)
                        logging.debug("Results: {}".format(objs))
                        for obj in objs:
                            next_v = v.make(root=obj, stack=stack+[obj])
                            vals.append(next_v)
                else:
                    vals = [v]
                newobj_dict[k] = vals

        newobj_dict['id'] = root
        newobj_dict['_keys'] = list(newobj_dict.keys())
        if cls_name is None:
            cls_name = 'Thing'

        logging.debug("Making new cls t: {}".format(cls_name))
        cls = type(cls_name,(Thing,),newobj_dict)
        newobj = cls()
        for k,v in newobj_dict.items():
            newobj.__setattr__(k,v)
        return newobj

class Crawler:
    """
    Abstract superclass of all data crawlers
    """
    pass

class RdflibCrawler(Crawler):
    def __init__(self,graph=None):
        self.graph = graph
        
    def crawl(self, subj, pred):
        usubj = URIRef(subj)
        upred = URIRef(pred)
        logging.debug("Querying rdflib for {} {} // {} {}".format(usubj, upred, type(usubj), type(upred)))
        return [self.toPython(o) for (s,p,o) in self.graph.triples((usubj,upred,None))]

    def toPython(self, x):
        if isinstance(x,URIRef):
            return x.toPython()
        else:
            return x


class EndpointCrawler(Crawler):
    """
    Crawler that uses a REST service or other HTTP endpoint
    """
    pass

class SparqlCrawler(EndpointCrawler):
    """
    Crawler that uses a SPARQLWrapper object; typically remote
    """
    def __init__(self,sparql=None):
        self.sparql = sparql
        
    def crawl(self, subj, pred):
        from SPARQLWrapper import SPARQLWrapper, JSON
        sparql = self.sparql
        q = "SELECT ?o WHERE {{ <{s}> <{p}> ?o }}".format(s=subj, p=pred)
        logging.info("CRAWL: {}".format(q))
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        logging.info("CRAWL_RES={}".format(results))
        return [r['o']['value'] for r in results['results']['bindings']]


class NeoBoltCrawler(EndpointCrawler):
    pass

