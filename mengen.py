#!/usr/bin/env python3

from argparse import ArgumentParser
import subprocess
import shlex
import yaml

default_menu = 'dmenu -i -l 20'

def evaluate(env, item):
    if 'cmd' in item:
        subprocess.call(env + item['cmd'], shell=True)
    if 'men' in item:
        print(item['men'])
        men_args = [subprocess.check_output(
            '%s echo %s' % (env, a), shell=True).decode('utf-8').strip('\n')
            for a in shlex.split(item['men'])]
        args.start = men_args[0]
        args.arg = men_args[1:]
        print(men_args)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('start', nargs='?', default='main')
    parser.add_argument('arg', nargs='*', default=[])
    args = parser.parse_args()

    f = open(args.infile)
    data = yaml.load(f)
    f.close()

    while args.start:
        menudata = data[args.start]
        args.start = None

        env = ''
        if 'args' in menudata:
            n = min(len(menudata['args']), len(args.arg))
            for x in range(n):
                env += '%s="%s";' % (menudata['args'][x], args.arg[x])
        items = ''
        item_dict = {}
        if 'items' in menudata:
            for item in menudata['items']:
                if 'txt' in item:
                    key = subprocess.check_output(
                            'echo %s' % item['txt'], shell=True).decode('utf-8')
                    items += key
                    item_dict[key] = item
                elif 'gen' in item:
                    gen_items = subprocess.check_output(
                            '%s echo "`%s`"' % (env, item['gen']),
                            shell=True).decode('utf-8')
                    items += gen_items
                    for line in gen_items.split('\n'):
                        item_dict[line + '\n'] = item
        items = items.replace('"', '\\"').strip()
        try:
            selection = subprocess.check_output(
                    'echo "%s" | `[ -z "$menu" ] && echo "%s" || echo "$menu"`'
                    % (items, default_menu),
                    shell=True).decode('utf-8')
        except subprocess.CalledProcessError:
            selection = ''

        env += 'item="%s";' % selection.strip()
        if selection in item_dict:
            evaluate(env, item_dict[selection])
        else:
            evaluate(env, menudata)
