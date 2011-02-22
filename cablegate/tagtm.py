# -*- coding: utf-8 -*-
#
# Donated to the public domain by Lars Heuer - <heuer[at]semgia.com>
#
from __future__ import with_statement
import os
import re
import codecs
from datetime import date
from StringIO import StringIO
from urllib import quote

_NAMESPACES = {
    'cg': 'http://psi.metaleaks.org/cablegate/',
    'onto': 'http://psi.metaleaks.org/cablegate/onto/',
    'subj': 'http://psi.metaleaks.org/cablegate/subject-tag/',
    'org': 'http://psi.metaleaks.org/cablegate/organization-tag/',
    'program': 'http://psi.metaleaks.org/cablegate/program-tag/',
    'dc': 'http://purl.org/dc/elements/1.1/',
}

_FILES = (
    # (filename, prefix, type)
    ('subject-tags.txt', 'subj', 'onto:subject-tag'),
    ('program-tags.txt', 'program', 'onto:program-tag'),
    ('organization-tags.txt', 'org', 'onto:organization-tag'),
)


_TAG_NAME_PATTERN = re.compile(ur'^([A-Za-z0-9&/ _-]+)(?:[ \t]+)(.+)$', re.UNICODE)
_WS_NORMALIZER_PATTERN = re.compile(r'[ ]+')

def read_tags(filename):
    route_pattern = re.compile('^(R[A-Z]+)[ \t]+(.+)$')
    with codecs.open(filename, 'rb', 'utf-8') as f:
        for l in f:
            l = l.rstrip()
            if not l or l.startswith('#'):
                continue
            tag, name = _TAG_NAME_PATTERN.match(l).groups()
            tag = _WS_NORMALIZER_PATTERN.sub(' ', tag.strip().upper())
            yield tag, name

def generate_ctm(source_filename, fileobj, prefix, type):
    """\
    
    `fileobj`
        A file object.
    """
    def write_tags(source_filename, seen_tags, dupl_tags, prefix, type):
        for sid, tag, name in _get_sid_tag_name(source_filename, prefix):
            if sid in seen_tags:
                fileobj.write('# CAUTION: Duplicate\n')
                if sid not in dupl_tags:
                    dupl_tags.append(sid)
            else:
                seen_tags.append(sid)
            fileobj.write(u'''%s isa %s;
    - "%s";
    - dc:title: "%s".\n\n''' % (sid, type, tag, name))
    fileobj.write(u"""\
#
# ==============
# Cablegate TAGS
# ==============
#
#
# Description:  This topic map assigns names to TAGS
#
# License:      Public Domain
#
# Source:       <https://cabletags.wordpress.com/>
#
# Date:         2011-01-04
#
# Modified:     %s
# 

#
# Prefixes
#
%s


""" % (date.today().isoformat(), '\n'.join(sorted(['%prefix ' + k + ' <' + v + '>' for k, v in _NAMESPACES.iteritems()]))))
    seen_tags = []
    dupl_tags = []
    write_tags(filename, seen_tags, dupl_tags, prefix, type)
    if dupl_tags:
        fileobj.write('\n\n# Duplicates: %r\n' % dupl_tags)


def _get_sid_tag_name(filename, prefix):
    """\
    Returns a tuple (sid, tag, name) where "sid" is either an IRI or a QName.

    `filename`
        The file to read the tags/names from (tag <tab> name).
    """
    for tag, name in read_tags(filename):
        path = quote(tag).replace(u'/', u'%2F')
        if path == tag:
            sid = u'%s:%s' % (prefix, tag)
        else:
            sid = u'<%s%s>' % (_NAMESPACES.get(prefix), path)
        yield sid, tag, name


if __name__ == '__main__':
    import codecs
    for filename, prefix, type in _FILES:
        ctm_filename = filename.replace('.txt', '.ctm')
        generate_ctm('./' + filename, codecs.open('./' + ctm_filename, 'wb', 'utf-8'), prefix, type)
