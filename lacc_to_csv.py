#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import re
import re
import os
import sys
import optparse
import glob
import csv
import time

            
class processcc(object):
    """ Class to process Closed-caption news data
    """
    # Pseudocode for coding news story data
    # Author: Gaurav Sood

    # Structure of the data
    #  Each file contains data for one news program
    #  File name carries information about the date, channel, name of the news program
    #  News story data on lines that start with CCO
    #  Relevant meta data on lines starting with TOP, UID, DUR, 
    #  Each news program has news stories: lines with XDS convery the news story break
    #  lines starting with OTS seem to be blank

    def __init__(self, path_to_filename, options):
        self.options = options
        with open(path_to_filename, "r") as f:
            self.lines = f.readlines()
            self.text = ''.join(self.lines)
        self.stories = []
        self.norm_stories = []
        self.absfilepath = os.path.abspath(path_to_filename)
    
    # This function's job is to get all the relevant metadata for each of the news programs
    def getmetadata(self):
        result = []
        header = ""
        for i in range(10):
            try:
                header += self.lines[i]
            except:
                break
        #get channel name #(see the first line, also in the name of the file - for instance, MSNBC)
        #get program name #(see the first line, also in the name of the file - for instance, Scarborough Country) 
        r = re.findall('^TOP\|\d+\|\d{4}\-\d{2}\-\d{2}_\d{4}_([^_]+)(.*)$', header, re.M)
        if r:
            result.append(r[0][0])
            result.append(r[0][1].replace('_', ' ').strip())
        else:
            result.append('NA')
            result.append('NA')

        #get UID # UID line
        r = re.findall('^UID\|([0-9a-fA-F\-]+)', header, re.M)
        if r:
            result.append(r[0])
        else:
            result.append('NA')

        #get duration # (in the 'dur')
        r = re.findall('^DUR\|([0-9\:]+)', header, re.M)
        if r:
            result.append(r[0])
        else:
            result.append('NA')

        #get year #(the LBT line XYZ PST)
        #get day  # LBT line
        #get date # LBT line
        #get time of start of broadcast 
        #get timezone # in the LBT line - it is the "PST" or "EST")
        r = re.findall('^LBT\|(\d+)\-(\d+)\-(\d+)\s+([0-9\:]+)\s+(.*)$', header, re.M)
        if r:
            for a in r[0]:
                result.append(a)
        else:
            for a in range(5):
                result.append('NA')

        #get path # filepath ane name
        result.append(self.absfilepath)
        #get wordcount (this is from a separate wordcount file)
        filename, ext = os.path.splitext(self.absfilepath)  # @UnusedVariable
        filename += '.wc'
        try:
            f = open(filename, 'r')
            wc = f.readline().strip()
            f.close()
        except:
            wc = 'NA'
        result.append(wc)

        return result
        
    # Function converts each news program to a list of news stories (separated by XDS)
    # Each Program resides in a separate file hence it takes path_to_filename as input
    def text_to_story(self):
        #look for XDS|  
        #if non XDS| - there is only element in the list
        #output list of stories
        #### XDS|20120301085700|%   LENGTH: 0:51:00 of 1:04:00
        ##### NO LONGER NEED TO SPLIT STORY ###
        #self.text = re.sub(r'(XDS\|\d+\|\%\s+LENGTH\:\s+\d+\:\d+:\d+\s+of\s+\d+\:\d+:\d+)', '', self.text)
        #self.stories = re.split(r"\s(?=XDS\|)", self.text)
        self.stories = [self.text]
        return self.stories

    # This function normalizes text of a story
    def normalize(self):
        self.norm_stories = []
        for s in self.stories:
            # Replace decimal period with 'dot' to avoid sentence split
            s = re.sub(r'(CCO|OTS|TR0|CC1|CC2)+[\d|\.]+', '', s)
            s = re.sub(r'(TOP|COL|UID|DUR|CMT|LBT|XDS|END|SegStart)+\|.*\n?', '', s)
            s = re.sub("\s\.", '.', s)
            if len(s):
                self.norm_stories.append(s)
        return self.norm_stories


def parse_command_line(argv):
    """Parse command line options
    """
    usage = "Usage: %prog [options] <directory of text files>"                
    parser = optparse.OptionParser(add_help_option=True, usage=usage)
    
    parser.add_option("-o", "--out", action="store", 
                      type="string", dest="outfile", default="program.data.csv",
                      help="Output file in CSV (default: program.data.csv)")
    
    return parser.parse_args(argv)

"""Constant declaration
"""
META_HEADER = ['channel.name', 'program.name', 'uid', 'duration', 'year', 'month', 'date', 'time', 'timezone', 'path', 'wordcount', 'text']

if __name__ == "__main__":
    print("Parse CC files to a single CSV file")
    (options, args) = parse_command_line(sys.argv)

    print("Command: " + ' '.join(sys.argv))
    print("Options ==> %s\nArgs ==> %s\n" % (options, args))

    if len(args) < 2:
        print("Usage: %s [options] <directory of text files>\n" % (sys.argv[0]))
        sys.exit(-1)
   
    csvfile = open(options.outfile, 'w')    
    csvwriter = csv.writer(csvfile, dialect='excel', delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    """Write headers
    """
    csvwriter.writerow(META_HEADER)
                
    count = 0
    all_start = time.time()
    # for file in folder
    for root, dirnames, filenames in os.walk(args[1]):
        for filename in glob.glob(root + '/*.txt'):
            count += 1
            pp = processcc(filename, options)
            print("#%d: %s" % (count, filename))
            # Get all the meta data and put it in the csv
            meta = pp.getmetadata()
            # Convert each program to a list of stories
            stories = pp.text_to_story()
            stories = pp.normalize()
            # for each story
            for story in stories:
                c = meta[:]
                c.append(story)
                csvwriter.writerow(c)
    csvfile.close()
