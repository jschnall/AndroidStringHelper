#!/usr/bin/python
# coding: utf8
import sys, getopt
import csv
import os
import errno
import re
import StringIO
import json

'''
Tool to compare 2 CSV files for missing strings
'''


def show_usage():
    print 'csvdiff.py -i <inputFile1> -j <inputFile2> -d'

# Convert strings.csv to Android strings.xml
def print_diff(inpath, inpath2, delim):
    names = read_csv(inpath, delim)
    names2 = read_csv(inpath2, delim)

    s = set(names2)
    result = [x for x in names if x not in s]
    print str(len(result)) + ' differences found.'
    print result

def read_csv(inpath, delim):
    names = []
    translates = []
    outdirs = []
    strings = []

    #read data from csv file
    csvfile = open(inpath)
    content = csvfile.read().replace('\\', '\\\\').replace('""', '\\"')
    readCSV = csv.reader(StringIO.StringIO(content), doublequote=False, escapechar='\\', delimiter=delim)

    # read header row
    header = readCSV.next()
    for cell in header[2:]:
        outdirs.append(cell)
        strings.append([])
    # read data rows
    for row in readCSV:
        names.append(row[0])
        translates.append(row[1])
        i = 0
        for cell in row[2:]:
            strings[i].append(cell.decode('utf-8'))
            i += 1
    csvfile.close()
    return names



def replace_special_chars(s):
    s = s.replace('&', '&amp;')
    s = s.replace('...', '&#8230;')
    # replace curly quotes with straight quotes
    s = re.sub(r'[“”]', r'"', s)
    # replace less than except when part of html tag
    s = re.sub(r'<(?!(a href)|/a>)', '&lt;', s)

    # escape apostrophes
    s = re.sub(r"(?<!\\)'", r"\'", s)
    # escape double quotes: Don't think this is necessary. Removed because it broke html tags
    # s = re.sub(r'(?<!\\)"', r'\"', s)

    return s

def main(argv):
    # Instead of the following hack, use .decode('utf-8') on all input, and .encode('utf-8') on all output
    #reload(sys)
    #sys.setdefaultencoding('utf8')

    # Defaults
    inpath = ''
    inpath2 = ''
    delimiter = ','

    try:
        opts, args = getopt.getopt(argv, 'hi:j:')
    except getopt.GetoptError:
        show_usage()
        sys.exit(2)
    if not opts:
        show_usage()
        sys.exit(2)
    keys = [index[0] for index in opts]
    if not '-i' in keys:
        print 'Input file not specified.'
        show_usage()
        sys.exit(2)
    if not '-j' in keys:
        print 'Second Input file not specified'
        show_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_usage()
            sys.exit()
        elif opt == '-i':
            inpath = arg
        elif opt == '-j':
            inpath2 = arg
        elif opt == '-d':
            delimiter = arg

    #print('Input file: ', inpath)
    #print('Input file2: ', inpath2)

    print_diff(inpath, inpath2, delimiter)


if __name__ == "__main__":
    main(sys.argv[1:])
