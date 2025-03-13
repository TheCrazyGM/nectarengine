#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to write version information to hiveengine/version.py
"""
import sys

VERSION = '0.2.3'


def write_version_py(filename):
    """Write version."""
    cnt = """\"""THIS FILE IS GENERATED FROM HIVEENGINE PYPROJECT.TOML.\""\"\nversion = '%(version)s'\n"""
    with open(filename, 'w') as a:
        a.write(cnt % {'version': VERSION})


if __name__ == '__main__':
    write_version_py('hiveengine/version.py')
    print(f"Version {VERSION} written to hiveengine/version.py")
    sys.exit(0)
