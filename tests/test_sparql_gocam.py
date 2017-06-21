from ldconstructor import *

import logging
from ro import RelationOntology
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
import json
import yaml

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("http://rdf.geneontology.org/sparql")

fetchType = dict(a=follow(RDF.type,
                          label=follow(RDFS.label)))
                  
annoton = dict(enabled_by=follow(RelationOntology.enabled_by,
                                 **fetchType),
               occurs_in=follow(RelationOntology.occurs_in,
                                **fetchType),
               part_of=follow(RelationOntology.part_of,
                              **fetchType),
               **fetchType
)
sb = construct(causally_upstream_of=follow(RelationOntology.causally_upstream_of,
                                           **annoton),
               **annoton)

sb.crawler = SparqlCrawler(sparql=sparql)

def test_kinase():
    qt="SELECT ?i WHERE {{ ?i rdf:type <{funcCls}> }}"
    q = qt.format(funcCls=RelationOntology.kinase_activity)
    logging.info('QUERY={}'.format(q))
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print('RESULTS={}'.format(results))
    insts = [r['i']['value'] for r in results['results']['bindings']]
    objs = []
    for i in insts:
        obj = sb.make(root=i)
        print("-----")
        #print(str(json.dumps(obj.to_dict(),
        #                     sort_keys=True,
        #                     indent=4, separators=(',', ': '))))
        print(yaml.dump(obj.to_dict(), default_flow_style=False))
        with open("OUT.yaml","a") as myfile:
            myfile.write(yaml.dump(obj.to_dict(), default_flow_style=False))
        #print("......")
        #print(str(obj))
        objs.append(obj)
