#!/usr/bin/env python3

from argparse import ArgumentParser
import os.path
import subprocess
import shlex
import yaml

def evaluate(env, item):
    if 'cmd' in item:
        subprocess.call(env + item['cmd'], shell=True)
    if 'men' in item:
        men_args = [subprocess.check_output(
            '%s echo %s' % (env, a), shell=True).decode('utf-8').strip('\n')
            for a in shlex.split(item['men'])]
        args.start = men_args[0]
        args.arg = men_args[1:]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('-m', '--menu', default='dmenu -i -l 20')
    parser.add_argument('-i', '--idxopt', default='-si')
    parser.add_argument('start', nargs='?', default='main')
    parser.add_argument('arg', nargs='*', default=[])
    args = parser.parse_args()

    try:
        f = open(args.infile)
    except FileNotFoundError:
        f = open(os.path.expanduser('~/menu/%s.yml' % args.infile))
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
        if 'env' in menudata:
            for line in menudata['env']:
                env += '%s;' % line
        items = ''
        item_dict = {}
        if 'items' in menudata:
            for item in menudata['items']:
                if 'txt' in item:
                    key = subprocess.check_output(
                            '%s echo %s' % (env, item['txt']),
                            shell=True).decode('utf-8')
                    items += key
                    item_dict[key] = item
                elif 'gen' in item:
                    gen_items = subprocess.check_output(
                            '%s echo "$(%s)"' % (env, item['gen']),
                            shell=True).decode('utf-8')
                    items += gen_items
                    for line in gen_items.split('\n'):
                        item_dict[line + '\n'] = item
        items = items.replace('"', '\\"').strip('\n')
        menu = args.menu
        if 'idx' in menudata:
            idx = int(subprocess.check_output(
                    '%s echo %s' % (env, menudata['idx']), shell=True))
            menu += ' %s %i' % (args.idxopt, idx)
        try:
            selection = subprocess.check_output(
                    'echo "%s" | %s' % (items, menu),
                    shell=True).decode('utf-8')
        except subprocess.CalledProcessError:
            selection = ''

        env += 'item="%s";' % selection.strip()
        if selection in item_dict:
            evaluate(env, item_dict[selection])
        else:
            evaluate(env, menudata)
