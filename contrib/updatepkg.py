#!/usr/bin/env python

import os, sys, re, hashlib

ROOT = os.path.join(os.path.dirname(__file__), '..')
PKGBUILD = os.path.join(ROOT, 'contrib', 'PKGBUILD')
VER = re.compile('^pkgver=[\d\.]+$', re.M)
MD5 = re.compile("^md5sums=\('[0-9a-f]+'\)$", re.M)

sys.path.insert(0, ROOT)

if __name__ == '__main__':
    import opster
    dist = os.path.join(ROOT, 'dist', 'opster-%s.tar.gz' % opster.__version__)
    if not os.path.exists(dist):
        print 'dist .tar.gz is not built yet, exiting'
        sys.exit(1)

    pkg = open(PKGBUILD).read()
    pkg = VER.sub('pkgver=%s' % opster.__version__, pkg)
    md5 = hashlib.md5(open(dist).read()).hexdigest()
    pkg = MD5.sub("md5sums=('%s')" % md5, pkg)
    open(PKGBUILD, 'w').write(pkg)

    print 'PKGBUILD updated'
