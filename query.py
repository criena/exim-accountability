#!/usr/bin/env python3
#-*- coding: utf8 -*-
#
__author__ = 'Karel W. Dingeldey '
__copyright__ = 'Copyright (c) Criena Network'


################################################################################
### Imports
################################################################################

import logging, os, sys
import datetime, json, lzma, re

from systemd.journal import JournalHandler


################################################################################
### Variables
################################################################################

db_file = 'accountability.db'
targets_file = 'accountability.conf'
blacklist_file = 'accountability.blocklist'
local_part_regex = re.compile('^([a-zA-Z0-9.-]+)_([0-9]{8})')


################################################################################
### Functions
################################################################################

def main():

    # Read targets file
    try:
        with open(os.path.join(os.path.dirname(__file__), targets_file), 'rt') as fh:
            targets = json.load(fh)
    except Exception:
        log.exception(f'Failed to read targets file "{targets_file}"!')
        print('DEFER Failed to read targets file!')
        sys.exit(1)

    if len(sys.argv) != 3:
        # 2 arguments expected (local_part and domain)
        log.error(f'Wrong number of arguments provided ({len(sys.argv) - 1} instead of 2)!')
        print('DEFER Wrong number of arguments given!')
        sys.exit(0)

    local_part = sys.argv[1]
    domain = sys.argv[2]
    email_address = f'{local_part}@{domain}'

    if not domain in targets:
        # domain is not properly configured
        log.warning(f'Unknown domain "{domain}"!')
        print('DEFER Unknown domain!')
        sys.exit(0)

    result = re.match(local_part_regex, local_part)
    if not result:
        # local_part has the wrong format
        log.warning('Local part ({local_part}) does not match criteria.')
        print('DECLINE Local part does not match syntax!')
        sys.exit(0)

    try:
        if email_address in open(os.path.join(os.path.dirname(__file__), blacklist_file), 'rt').read().splitlines():
            # address found on blacklist
            print('FAIL Address blacklisted!')
            sys.exit(0)
    except Exception:
        log.warning(f'Failed to read blacklist file "{blacklist_file}".')

    print(f'REDIRECT {targets[domain]}')

    # Log the used address
    now = datetime.datetime.now(datetime.UTC)
    try:
        with lzma.open(os.path.join(os.path.dirname(__file__), db_file), 'at') as db:
            db.write(f'[{now.strftime("%Y-%m-%d %H:%M:%S")}] {email_address}\n')
    except Exception:
        log.error(f'Failed to amend database file "{db_file}".')


################################################################################
### Main
################################################################################

if __name__ == '__main__':

    # Set up logging
    try:
        log = logging.getLogger()
        log.addHandler(JournalHandler())
        log.setLevel(logging.INFO)
    except Exception:
        sys.stderr.write('Failed to set up logging!')
        sys.exit(1)

    main()
