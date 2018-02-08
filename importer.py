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
Tool to convert CSV files exported from Google Spreadsheets into Android Strings
'''


def show_usage():
    print 'helper.py -i <inputFile> -o <outputDir> -n [outputFileName] -d [delimiter] -t [strings|plurals|json]'


# Convert strings.csv file to JSON, using default translations as keys
def convert_json(inpath, outpath, outname, delim):
    names = []
    locales = []
    strings = []

    #read data from csv file
    csvfile = open(inpath)
    content = csvfile.read().replace('\\', '\\\\').replace('""', '\\"')
    readCSV = csv.reader(StringIO.StringIO(content), doublequote=False, escapechar='\\', delimiter=delim)

    # read header row
    header = readCSV.next()
    for cell in header[3:]:
        #print cell
        tokens = cell.split('-')
        if len(tokens) > 2:
            locales.append(tokens[1] + '-' + tokens[2][1:])
        elif len(tokens) > 1:
            locales.append(tokens[1])
        strings.append([])
    #print locales

    # read data rows
    for row in readCSV:
        names.append(row[2])
        i = 0
        for cell in row[3:]:
            strings[i].append(cell.decode('utf-8'))
            i += 1
    csvfile.close()

    # build dictionary
    result = {}
    for i in range(len(locales)):
        translations = {}
        locale = locales[i]
        values = strings[i]
        for j in range(len(names)):
            name = names[j]
            value = replace_special_chars(unicode(values[j])).encode('utf-8')
            translations[name] = value
        result[locale] = translations

    # write dictionary as json to file
    outfilename = os.path.join(outpath, outname)
    if not os.path.exists(os.path.dirname(outfilename)):
        try:
            os.makedirs(os.path.dirname(outfilename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    json_string = json.dumps(result, sort_keys=True, indent=4,
                             ensure_ascii=False)
    outfile = open(outfilename, "w")
    outfile.write(json_string)
    outfile.close()

# Convert plurals.csv to Android plurals.xml
def convert_plurals(inpath, outpath, outname, delim):
    names = []
    quantities = []
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
        quantities.append(row[1])
        i = 0
        for cell in row[2:]:
            strings[i].append(cell.decode('utf-8'))
            i += 1
    csvfile.close()

    # write Android plurals file
    for i in range(len(outdirs)):
        outdir = outdirs[i]
        outfilename = os.path.join(outpath + "/" + outdir, outname)
        if not os.path.exists(os.path.dirname(outfilename)):
            try:
                os.makedirs(os.path.dirname(outfilename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        outfile = open(outfilename, "w")
        outfile.write('<resources>\n')

        values = strings[i]
        value = replace_special_chars(unicode(values[0])).encode('utf-8')
        currentname = names[0]
        outfile.write('    <plurals name="' + currentname + '">\n')
        outfile.write('        <item quantity="' + quantities[0] + '">' + value + '</item>\n')
        for j in range(1, len(names)):
            name = names[j]
            quantity = quantities[j]
            value = replace_special_chars(unicode(values[j])).encode('utf-8')
            if name and currentname != name:
                # Finish old plural and start new one
                outfile.write('    </plurals>\n\n')
                currentname = name
                outfile.write('    <plurals name="' + currentname + '">\n')
                outfile.write('        <item quantity="' + quantity + '">' + value + '</item>\n')
            else:
                # Add quantity to current plural
                outfile.write('        <item quantity="' + quantity + '">' + value + '</item>\n')
        outfile.write('    </plurals>\n')
        outfile.write('</resources>')
        outfile.close()


# Convert strings.csv to Android strings.xml
def convert_strings(inpath, outpath, outname, delim):
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

    # write Android strings files
    for i in range(len(outdirs)):
        outdir = outdirs[i]
        outfilename = os.path.join(outpath + "/" + outdir, outname)
        if not os.path.exists(os.path.dirname(outfilename)):
            try:
                os.makedirs(os.path.dirname(outfilename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        outfile = open(outfilename, "w")
        outfile.write('<resources>\n')
        values = strings[i]
        for j in range(len(names)):
            name = names[j]
            translate = translates[j]
            value = replace_special_chars(unicode(values[j])).encode('utf-8')

            if outdirs[i] == 'values':
                # default values, include translatable
                if translate.lower() == 'false':
                    outfile.write('    <string name="' + name + '" translatable="' + translate.lower() +'">' + value + '</string>\n')
                else:
                    outfile.write('    <string name="' + name + '">' + value + '</string>\n')
            elif translate.lower() == 'true' and value:
                    outfile.write('    <string name="' + name + '">' + value + '</string>\n')
        outfile.write('</resources>')
        outfile.close()


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
    outname = ''
    delimiter = ','
    filetype = 'strings'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:n:d:t:')
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
    if not '-o' in keys:
        print 'Output directory not specified.'
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
        elif opt == '-n':
            outname = arg
        elif opt == '-d':
            delimiter = arg
        elif opt == '-t':
            filetype = arg

    #print('Input file: ', inpath)
    #print('Output directory: ', outpath)
    #print('Output filename: ', outname)
    #print('Delimiter: ', delimiter)
    #print('Type: ', type)

    if filetype.lower() == "strings":
        if not outname:
            outname = "strings.xml"
        convert_strings(inpath, outpath, outname, delimiter)
    elif filetype.lower() == "plurals":
        if not outname:
            outname = "plurals.xml"
        convert_plurals(inpath, outpath, outname, delimiter)
    elif filetype.lower() == "json":
        if not outname:
            outname = "strings.json"
        convert_json(inpath, outpath, outname, delimiter)


if __name__ == "__main__":
    main(sys.argv[1:])
