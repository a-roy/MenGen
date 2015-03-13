#!/usr/bin/env python3

from argparse import ArgumentParser
import subprocess
import yaml

default_menu = 'dmenu -i -l 20'

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('start', nargs='?', default='main')
    parser.add_argument('arg', nargs='*', default=[])
    args = parser.parse_args()

    f = open(args.infile)
    data = yaml.load(f)
    f.close()
    menudata = data[args.start]

    env = 'men="python3 %s %s";' % (__file__, args.infile)
    if 'args' in menudata:
        n = min(len(menudata['args']), len(args.arg))
        for x in range(n):
            env += '%s="%s";' % (menudata['args'][x], args.arg[x])
    items = ''
    if 'items' in menudata:
        for item in menudata['items']:
            items += subprocess.check_output(
                    'echo %s' % item['txt'], shell=True).decode('utf-8')
    if 'gen' in menudata:
        gen = menudata['gen']
        items += subprocess.check_output(
                '%s echo "`%s`"' % (env, gen), shell=True).decode('utf-8')
    items = items.replace('"', '\\"').strip()
    try:
        selection = subprocess.check_output(
                'echo "%s" | `[ -z "$menu" ] && echo "%s" || echo "$menu"`'
                % (items, default_menu),
                shell=True).decode('utf-8')
    except subprocess.CalledProcessError:
        selection = ''

    env += 'item="%s";' % selection.strip()
    if 'items' in menudata:
        item_dict = { subprocess.check_output(
                    'echo %s' % item['txt'], shell=True).decode('utf-8') :
                    item['cmd'] for item in menudata['items'] }
        if selection in item_dict:
            subprocess.call(env + item_dict[selection], shell=True)
        elif 'cmd' in menudata:
            subprocess.call(env + menudata['cmd'], shell=True)
    elif 'cmd' in menudata:
        subprocess.call(env + menudata['cmd'], shell=True)
