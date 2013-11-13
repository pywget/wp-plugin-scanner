wp-plugin-scanner
=================

WordPress Plugin Scanner

usage: wp-plugin-scan.py [-h] [-s <website url>] [-u <page number>]
                         [-p <seconds>] [-t <thread count>]
                         [-l <plugin list path>]

Scan any wordpress powered website and identify plugins installed. Originally taken from https://github.com/an1zhegorodov/WP-plugin-scanner, modified by pywget.

optional arguments:
  -h, --help            show this help message and exit
  -s <website url>, --scan <website url>
                        scan website at <website url>
  -u <page number>, --update <page number>
                        update the list of plugins from wordpress.org up to <page number>
  -p <seconds>, --pause <seconds>
                        sleep (in seconds) between each request, default: 0
  -t <thread count>, --threads <thread count>
                        scanning threads, default: 1
  -l <plugin list path>, --list <plugin list path>
                        path to wp plugin list separated by newline, default: plugin.txt
