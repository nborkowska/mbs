#!/usr/bin/env python

import linecache, shlex
from optparse import OptionParser

class FileMerger(object):

    MISSED = '?'
    LOOP = 'loop_'
    KEY = '_'
    MULTIPLE = ';'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def getMissedKeys(self):
        
        refFile = open(self.refFile, 'r')
        skip = False
        currentKey = self.KEY # initialize an empty key
        missedInfo = {} #where key is a missed key and a value is a line number
        
        for index, line in enumerate(refFile.readlines()):
            parts = shlex.split(line)
            
            if len(parts) == 0: #empty line, breaks the loop
                skip = False
            
            elif len(parts) == 1:    
                if parts[0] == self.LOOP or skip:
                    skip = True    
                elif parts[0][0] == self.KEY: 
                    currentKey = parts[0]
                elif parts[0] == self.MISSED:
                    missedInfo[currentKey] = index
            
            elif parts[0][0] == self.KEY and parts[1] == self.MISSED:
                currentKey = parts[0]
                missedInfo[currentKey] = index
        
        refFile.close()
        return missedInfo

    def getMissedValues(self, keys):
        
        expFile = open(self.expFile, 'r')
        currentKey = self.KEY # initialize an empty key
        missedInfo, additional = {}, []
        missed = False
        cntr = 0
        
        for line in expFile.readlines():
            parts = shlex.split(line)
            
            if parts and parts[0] in keys.keys():
                currentKey = parts[0]
                if len(parts) > 1:
                    missedInfo[currentKey] = parts[1]
                    missed = False
                else:
                    missed = True
            
            elif parts and missed:
                if parts[0] != self.MULTIPLE:
                    currentValue = missedInfo.get(currentKey, '')
                    missedInfo[currentKey] = '%s\n%s' % (currentValue, line)
                elif cntr % 2:
                    missed = False
                    cntr += 1
            else:
                additional.append(line)

        expFile.close()
        return missedInfo, additional
    
    def fillMissedInfo(self, keys, info, additional):
        output = open(self.outName, 'w')
        refFile = open(self.refFile, 'r')
        prevLines = ['','','']

        for index, line in enumerate(refFile.readlines()):
            prevLines = prevLines[1:]
            prevLines.append(line)
            if index in keys.values():
                if prevLines[1] == self.MULTIPLE:
                    newLine = info.get(prevLines[0], self.MISSED)
                else:
                    parts = shlex.split(line)
                    newLine = '%s\t%s' % (parts[0], \
                            info.get(parts[0], self.MISSED))
                if newLine[-1] == '\n':
                    newLine = newLine[:-1]

                output.write('%s\n' % newLine)
            else:
                output.write('%s\n' % line)
        print keys.keys()
        refFile.close()
        for line in additional:
            output.write('%s' % line)
        """ to jest totalnie zle nie tylko jesli chodzi o znaki nowej linii
            ale i o klucze bo jest np w outpucie 2 razy audit_creation_method
            Bo jesli nie ma klucza w poszukiwanych, to wcale nie musimy tego dawac do additional,
            tylko wtedy gdy nie jest to klucz ani jego wartosc...
        """
        output.close()

    def merge(self):
        missedKeys = self.getMissedKeys()
        missedValues, additionalInfo = self.getMissedValues(missedKeys)
        self.fillMissedInfo(missedKeys, missedValues, additionalInfo)
        
def valid(options):
    """ Check mandatory params """

    for val in options.__dict__.values():
        if val is None:
            return False

    return True

def main():

    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-r", "--ref", type="string", dest="refFile", \
            help='.cif reference data file')
    parser.add_option("-e", "--exp", type="string", dest="expFile", \
            help='.cif experimental data file')
    parser.add_option("-o", "--out", type="string", dest="outName", \
            help='output filename')
    
    (options, args) = parser.parse_args()

    if not valid(options):
        parser.print_help()
        return 0

    m = FileMerger(**options.__dict__)
    m.merge()

if __name__ == '__main__':
    main()
