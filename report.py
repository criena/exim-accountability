#!/usr/bin/env python3
#-*- coding: utf8 -*-
#
__author__ = 'Karel W. Dingeldey '
__copyright__ = 'Copyright (c) Criena Network'


################################################################################
### Imports
################################################################################

import logging, os, sys
import json, lzma, re, smtplib

from systemd.journal import JournalHandler
from email.message import Message


################################################################################
### Variables
################################################################################

db_file = 'accountability.db'
targets_file = 'accountability.conf'
email_regex = re.compile('((.+)_([0-9]{8}))@(.+)')
email_from = '"Criena Network E-Mail System" <admin@criena.net>'


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
        sys.exit(1)

    # Set up reports draft
    reports = {}
    for domain in targets.keys():
        reports[domain] = []

    # Open database file
    try:
        db = lzma.open(os.path.join(os.path.dirname(__file__), db_file), 'rt')
    except Exception:
        log.error(f'Failed to amend database file "{db_file}".')
    else:

        # Go through each line of the database
        for line in db:
            try:
                fields = line.split()
            except:
                log.warning(f'Line does not match criteria ("{line}")!')
                continue

            address = fields[2]
            result = re.match(email_regex, address)
            if not result:
                log.warning(f'Address does not match regular expression ("{address}")!')
                continue

            local_part = result.group(1)
            domain = result.group(4)

            if domain in reports.keys():
                if not address in reports[domain]:
                    reports[domain].append(address)

        db.close()

    # Sending emails
    for domain in reports.keys():
        chronological_order = f'The below addresses have been used (in chronological order):\n\n'
        chronological_order += '\n'.join(reports[domain])
        alphabetical_order = f'The below addresses have been used (in alphabetical order):\n\n'
        reports[domain].sort()
        alphabetical_order += '\n'.join(reports[domain])

        msg = f'From: {email_from}\n'
        msg += f'To: <{targets[domain]}>\n'
        msg += f'Subject: Accountability report for {domain} ({len(reports[domain])} entries)\n'
        msg += alphabetical_order
        msg += '\n' * 3
        msg += chronological_order

        s = smtplib.SMTP('localhost')
        s.sendmail(email_from, targets[domain], msg)
        s.quit()


################################################################################
### Main
################################################################################

if __name__ == '__main__':

    # Set up logging
    try:
        log = logging.getLogger()
        log.addHandler(JournalHandler())
        log.setLevel(logging.WARNING)
    except Exception:
        sys.stderr.write('Failed to set up logging!')
        sys.exit(1)

    main()
