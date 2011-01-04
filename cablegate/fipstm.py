# -*- coding: utf-8 -*-
#
# Donated to the public domain by Lars Heuer - <heuer[at]semgia.com>
#
import re
import codecs
from datetime import date
from StringIO import StringIO
from urllib import quote


def generate_ctm(fileobj):
    """\
    
    `fileobj`
        A file object.
    """
    fileobj.write(u"""\
#
# ========
# Geo TAGS
# ========
#
# Description:  Geo-Political TAGS acc. to
#               U.S. Department of State Foreign Affairs Handbook Volume 5 
#               TAGS/Terms Handbook
#
# Author:       Lars Heuer <heuer[at]semagia.com>
#
# License:      Public Domain
#
# Source:       <http://www.state.gov/documents/organization/89257.pdf>
#               <https://github.com/heuer/topicmaps/blob/master/cablegate/fips_regions.txt>
#               <https://github.com/heuer/topicmaps/blob/master/cablegate/name_fips_regions.txt>
#
# Date:         %s
# 

%%prefix tag <http://psi.metaleaks.org/cablegate/tag/>
%%prefix onto <http://psi.metaleaks.org/cablegate/ontology/>
%%prefix dc <http://purl.org/dc/elements/1.1/>


""" % date.today().isoformat())
    seen_tags = []
    dupl_tags = []
    fileobj.write("""\

def belongs-to($tag, $region)
    #TODO
end

#
# ---------
# Countries
# ---------
#
""")
    for code, name, regions in get_countries():
        fileobj.write(u'tag:%s isa onto:country-tag;\n    - "%s";\n    - dc:title: "%s";\n' % (code, code, name))
        for region in regions:
            fileobj.write(u'    belongs-to(tag:%s);\n' % region)
        fileobj.write(u'.\n\n')
    fileobj.write("""\
#
# -------
# Regions
# -------
#
""")
    for code, name in get_regions():
        fileobj.write(u'tag:%s isa onto:region-tag;\n    - "%s";\n    - dc:title: "%s".\n\n' % (code, code, name))


def get_countries():
    """\
    Returns (COUNTRY-CODE, COUNTRY-NAME, REGIONS) tuples.
    """
    p = re.compile(r'^(.+?)[ ]([A-Z]{2})[ ](.+)$', re.UNICODE)
    for l in codecs.open('./name_fips_regions.txt', 'rb', 'utf-8'):
        if l.startswith('#'):
            continue
        name, fips, regions = p.match(l).groups()
        regions = [r.strip() for r in regions.split(u',')]
        yield fips, name, regions


def get_regions():
    """\
    Returns (REGION-CODE, REGION-NAME) tuples
    """
    p = re.compile('^([A-Z]{2})[ ](.+)$')
    for l in open('./fips_regions.txt', 'rb'):
        if l.startswith('#'):
            continue
        fips, name = p.match(l).groups()
        yield fips, name.strip()


if __name__ == '__main__':
    import codecs
    generate_ctm(codecs.open('./geo-tags.ctm', 'wb', 'utf-8'))
