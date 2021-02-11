# exim-accountability

The idea is to have a unique email alias for every online account that requires an email address (Amazon, LinkedIn, ...). A dedicated domain is needed for each user/mailbox.

In case spam is received on one of the used email aliases, either the online service was breached and data was "stolen" or the company/organisation sold its users' data. In that case a new email alias can be assigned and the blown one should be put on the blocklist.

## Configuration file

The program expects a configuration file "accountability.conf" in JSON format as per below:

```
{
  "accountability-domain.com": "farrokh@bulsara.com"
}
```

In this example all emails in the format IDENTIFIER1_IDENTIFIER2@accountability-domain.com will be forwarded to farrokh@bulsara.com (unless included in the blocklist).

IDENTIFIER1 can be freely choosen, e.g. amazon or linkedin.com.

IDENTIFIER2 has to consist of 8 digits. It's perfect to use for a date (the date when you start using this alias), but any format is accepted.

## Exim integration

```
accountability_email:
  debug_print                     = "R: accountability_email for $local_part@$domain"
  driver                          = queryprogram
  domains                         = +accountability_domains
  command                         = /path/to/exim-accountability/query.py ''${quote:$local_part} ''${quote:$domain}
  command_user                    = ${config.services.exim.user}
  condition                       = ''${if match{$local_part}{^.+_\\d\{8\}}}
  timeout                         = 2s
```

## Reporting

A regular reporting can be set up by scheduling the periodic execution of report.py.
