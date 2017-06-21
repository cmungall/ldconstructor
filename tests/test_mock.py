from ldconstructor import *

class MockCrawler(Crawler):
    def crawl(self, subj, pred):
        if subj is None:
            raise ValueException()
        return ['{}-{}-1'.format(subj,pred),'x2']


def test_basic():
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

    assert True == True
    sb.crawler = MockCrawler()
    obj = sb.make()
    print(str(obj))
    import json
    print(str(json.dumps(obj.to_dict(),
                         sort_keys=True,
                         indent=4, separators=(',', ': '))))
