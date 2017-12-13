#!/usr/bin/python
# coding: utf8
import sys, getopt
import csv
import os
import errno
import re

'''
Tool to convert CSV files
'''

def showUsage():
    print 'helper.py -i <inputFile> -o <outputDir> -n [outputFileName] -d [delimiter]'

def convert(inpath, outpath, outname, delim):
    names = []
    translates = []
    outdirs = []
    strings = []

    #read data from csv file
    csvfile = open(inpath)
    readCSV = csv.reader(csvfile, delimiter=delim)
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
            strings[i].append(cell)
            i += 1
    csvfile.close()

    # write Android xml files
    i = 0
    for dir in outdirs:
        outfilename = os.path.join(outpath + "/" + dir, outname)
        if not os.path.exists(os.path.dirname(outfilename)):
            try:
                os.makedirs(os.path.dirname(outfilename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        outfile = open(outfilename, "w")
        outfile.write('<resources>\n')
        values = strings[i]
        j = 0
        for name in names:
            translate = translates[j]
            value = replaceSpecialChars(str(values[j]))

            if outdirs[i] == 'values':
                # default values, include translatable
                if translate == 'FALSE':
                    outfile.write('    <string name="' + name + '" translatable="' + translate +'">' + value + '</string>\n')
                else:
                    outfile.write('    <string name="' + name + '">' + value + '</string>\n')
            elif translate == 'TRUE' and value:
                    outfile.write('    <string name="' + name + '">' + value + '</string>\n')
            j += 1
        outfile.write('</resources>')
        outfile.close()
        i += 1

def replaceSpecialChars(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('...', '&#8230;')
    # replace curly quotes with straight quotes
    s = re.sub(r'[“”]', r'"', s)

    # escape apostrophes and quotes
    s = re.sub(r"(?<!\\)'", r"\'", s)
    s = re.sub(r'(?<!\\)"', r'\"', s)

    return s

def main(argv):
    #inpath = '/Users/jschnall/Documents/foo.csv'
    #outpath = '/Users/jschnall/Documents/res'
    inpath = ''
    outpath = ''
    outname = 'strings.xml'
    delimiter = ','

    try:
        opts, args = getopt.getopt(argv, 'hi:o:n:d:')
    except getopt.GetoptError:
        showUsage()
        sys.exit(2)
    if not opts:
        showUsage()
        sys.exit(2)
    keys = [index[0] for index in opts]
    if not '-i' in keys:
        print 'Input file not specified.'
        showUsage()
        sys.exit(2)
    if not '-o' in keys:
        print 'Output directory not specified.'
        showUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            showUsage()
            sys.exit()
        elif opt == '-i':
            inpath = arg
        elif opt == '-o':
            outpath = arg
        elif opt == '-n':
            outname = arg
        elif opt == '-d':
            delimiter = arg

    #print('Input file: ', inpath)
    #print('Output directory: ', outpath)
    #print('Output filename: ', outname)
    #print('Delimiter: ', delimiter)
    convert(inpath, outpath, outname, delimiter)

if __name__ == "__main__":
    main(sys.argv[1:])
