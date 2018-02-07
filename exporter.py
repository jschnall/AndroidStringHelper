#!/usr/bin/python
# coding: utf8
import sys, getopt
import csv
import os
import errno
import re
from xml.dom import minidom

'''
Tool to convert CSV files exported from Google Spreadsheets into Android Strings
'''


def show_usage():
    print 'helper.py -i <resDir> -o <outputDir> -d [delimiter]'


# Convert Android strings.xml to csv
def convert_strings(inpath, outpath, delim):
    # Create CSV file

    names = []
    translates = []
    values = []
    headers = []
    translations = []

    infile = os.path.join(inpath, 'values', 'strings.xml')
    if os.path.isfile(infile):
        names, translates, values = convert_values(infile)
    else:
        print "file does not exist: " + infile
        return

    # Loop through values folders in resource directory
    for root, dirs, files in os.walk(inpath):
        for dir in dirs:
            if dir.startswith('values-'):
                #print dir
                headers.append(dir)
                infile = os.path.join(inpath, dir, 'strings.xml')
                if os.path.isfile(infile):
                    #print infile
                    translations.append(convert_string_translations(infile))

    outfile = os.path.join(outpath, 'strings.csv')
    with open(outfile, 'wb') as outfile:
        writer = csv.writer(outfile, delimiter=delim)
        # Write header row
        row = ['name', 'translatable', 'values']
        row += headers
        writer.writerow(row)
        for i in range(len(names)):
            # Write name and each of it's translations
            name = names[i]
            translate = translates[i]
            value = values[i].encode('utf-8')
            row = [name, translate, value]
            for translation in translations:
                if translation.has_key(name):
                    row.append(translation[name].encode('utf-8'))
                else:
                    row.append('')
            writer.writerow(row)


# Read data from strings.xml file
# returns (name, translatable, string)
def convert_values(inpath):
    names = []
    translates = []
    values = []

    xmldoc = minidom.parse(inpath)
    strlist = xmldoc.getElementsByTagName('string')
    for str in strlist:
        names.append(str.attributes['name'].value)
        values.append(str.childNodes[0].nodeValue)
        if 'translatable' in str.attributes.keys():
            translates.append(str.attributes['translatable'].value)
        else:
            translates.append('true')
    return names, translates, values



# Read data from strings.xml file
# returns a dictionary of names and values
def convert_string_translations(inpath):
    dict = {}
    xmldoc = minidom.parse(inpath)
    strlist = xmldoc.getElementsByTagName('string')
    for str in strlist:
        name = str.attributes['name'].value
        value = str.childNodes[0].nodeValue
        dict[name] = value
    return dict


def convert_plurals(inpath, outpath, delim):
    # Create CSV file

    names = []
    quantities = []
    values = []
    headers = []
    translations = []

    infile = os.path.join(inpath, 'values', 'plurals.xml')
    if os.path.isfile(infile):
        names, quantities, values = convert_plural_values(infile)
    else:
        print "file does not exist: " + infile
        return

    # Loop through values folders in resource directory
    for root, dirs, files in os.walk(inpath):
        for dir in dirs:
            if dir.startswith('values-'):
                #print dir
                headers.append(dir)
                infile = os.path.join(inpath, dir, 'plurals.xml')
                if os.path.isfile(infile):
                    #print infile
                    translations.append(convert_plural_translations(infile))

    outfile = os.path.join(outpath, 'plurals.csv')
    with open(outfile, 'wb') as outfile:
        writer = csv.writer(outfile, delimiter=delim)
        # Write header row
        row = ['name', 'quantity', 'values']
        row += headers
        writer.writerow(row)
        oldname = ''
        for i in range(len(names)):
            # Write name and each of it's translations
            name = names[i]
            quantity = quantities[i]
            value = values[i].encode('utf-8')
            key = name + ',' + quantity
            if oldname == name:
                row = ['', quantity, value]
            else:
                row = [name, quantity, value]
            for translation in translations:
                if translation.has_key(key):
                    row.append(translation[key].encode('utf-8'))
                else:
                    row.append('')
            writer.writerow(row)
            oldname = name


def convert_plural_values(inpath):
    names = []
    quantities = []
    values = []

    xmldoc = minidom.parse(inpath)
    plurals = xmldoc.getElementsByTagName('plurals')
    for plural in plurals:
        name = plural.attributes['name'].value
        items = plural.getElementsByTagName("item")
        for item in items:
            names.append(name)
            quantities.append(item.attributes['quantity'].value)
            values.append(item.childNodes[0].nodeValue)
    return names, quantities, values


def convert_plural_translations(inpath):
    dict = {}

    xmldoc = minidom.parse(inpath)
    plurals = xmldoc.getElementsByTagName('plurals')
    for plural in plurals:
        name = plural.attributes['name'].value
        items = plural.getElementsByTagName("item")
        for item in items:
            quantity = item.attributes['quantity'].value
            value = item.childNodes[0].nodeValue
            key = name + ',' + quantity
            dict[key] = value
    return dict

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
    outpath = ''
    delimiter = ','

    try:
        opts, args = getopt.getopt(argv, 'hi:o:d:')
    except getopt.GetoptError:
        show_usage()
        sys.exit(2)
    if not opts:
        show_usage()
        sys.exit(2)
    keys = [index[0] for index in opts]
    if not '-i' in keys:
        print 'Resource directory not specified.'
        show_usage()
        sys.exit(2)
    if not '-o' in keys:
        print 'Output file not specified.'
        show_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_usage()
            sys.exit()
        elif opt == '-i':
            inpath = arg
        elif opt == '-o':
            outpath = arg
        elif opt == '-d':
            delimiter = arg

    #print('Input file: ', inpath)
    #print('Output directory: ', outpath)
    #print('Output filename: ', outname)
    #print('Delimiter: ', delimiter)
    #print('Type: ', type)

    convert_strings(inpath, outpath, delimiter)
    convert_plurals(inpath, outpath, delimiter)

if __name__ == "__main__":
    main(sys.argv[1:])
