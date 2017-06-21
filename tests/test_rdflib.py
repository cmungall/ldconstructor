from ldconstructor import *

import logging
logging.basicConfig(level=logging.DEBUG)
import yaml
import rdflib

fred = 'http://x.org/fred'
shuggy = 'http://x.org/shuggy'
knows = 'http://x.org/knows'
likes = 'http://x.org/likes'
livesIn = 'http://x.org/livesIn'
wormit = 'http://x.org/wormit'

def test_rdflib():
    sb = startFrom(fred,
                   knows=follow(knows,
                                livesIn=follow(livesIn)),
                   likes=follow(likes),
                   livesIn=follow(livesIn)
    )
    
    
    g = rdflib.Graph()
    g.parse('tests/resources/mini.ttl', format='turtle')
    
    #uri = rdflib.URIRef(fred)
    #print(uri)
    #for t in g.triples((uri,None,None)):
    #    print('T={}'.format(t))
    sb.crawler = RdflibCrawler(graph=g)
    obj = sb.make()
    print(str(obj))
    
    assert obj.id == fred
    fredKnows = obj.knows[0]
    print(fredKnows)
    assert fredKnows.id == shuggy
    assert fredKnows.livesIn[0].id == wormit
    
    P = dict(livesIn=follow(livesIn),
             likes=follow(likes))
    
    sb = startFrom(fred,
                   knows=follow(knows, **P),
                   **P
                   )
    sb.crawler = RdflibCrawler(graph=g)
    obj = sb.make()
    print(str(obj))
    print(yaml.dump(obj.to_dict(), default_flow_style=False))
    assert obj.id == fred
    fredKnows = obj.knows[0]
    print(fredKnows)
    assert fredKnows.id == shuggy
    assert fredKnows.livesIn[0].id == wormit
    
