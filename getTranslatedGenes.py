#!/usr/bin/python
"""Usage: getTranslatedGenes.py path/to/metagene/outfile.out path/to/contig/file.fasta /path/to/gene.fasta /path/to/ORF.fasta"""

import sys
#from itertools import tee, islice, izip_longest
import string

mgFile = open(sys.argv[1], 'r')
infasta = open(sys.argv[2], 'r')
geneFasta = open(sys.argv[3], 'w')
ORFfasta = open(sys.argv[4], 'w')
nucfasta = open(sys.argv[5], 'w')

def get_next_fasta (fileObject):
    '''usage: for header, seq in get_next_fasta(fileObject):
    '''
    header = ''
    seq = ''
    #The following for loop gets the header of the first fasta
    #record. Skips any leading junk in the file
    for line in fileObject:
        if line.startswith('>'):
            header = line.strip()
            break
    
    for line in fileObject:
        if line.startswith('>'):
            yield header, seq
            header = line.strip()
            seq = ''
        else:
            seq += line.strip()
    #yield the last entry
    if header:
        yield header, seq

def get_next(some_iterable, window=2):
    items, nexts = tee(some_iterable, 2)
    nexts = islice(nexts, window, None)
    return izip_longest(items, nexts)

#TRANS = { "T": "A", "A": "T", "G": "C", "C": "G" }

def complementary_strand(strand):
    return strand.translate(string.maketrans('TAGCtagc', 'ATCGATCG'))


transTab1L = {
'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'TTN': 'L', 
'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'TCN': 'S', 
'TAT': 'Y', 'TAC': 'Y', 'TAA': '.', 'TAG': '.', 
'TGT': 'C', 'TGC': 'C', 'TGA': '.', 'TGG': 'W', 
'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L', 'CTN': 'L', 
'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P', 'CCN': 'P', 
'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q', 
'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'CGN': 'R', 
'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M', 
'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T', 'ACN': 'T', 
'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 
'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 
'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V', 'GTN': 'V', 
'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A', 'GCN': 'A', 
'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E', 
'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G', 'GGN': 'G'
}


def translateDNA (seq, start=1, stop=None):
	'''This translates a DNA sequence from the start coordinate up to the stop
	coordinate. The assumption is that DNA sequence numbering begins at 1. It is
	also assumed that the sequence has already been 'cleaned'. This translation
	does not work with IUPAC degeneracy codes. The translation is carried out
	only as far as full codons are present, ie, the final one or two bases
	may be ignored. Currently, translation is only carried out in the forward
	direction. To translate the minus strand, the reverse complement sequence
	must be provided to this function. This function will convert the DNA
	sequence to upper case, however.
	
	>>> seq = 'atgcccgagtatgctcgcaatcgaaaatagcgctcatg'
	>>> translateDNA(seq)
	'MPEYARNRK.RS'
	>>> translateDNA(seq, start=2)
	'CPSMLAIENSAH'
	>>> translateDNA (seq, start=2, stop=17)
	'CPSML'
	
	'''
	
	if stop == None: stop = len(seq) 
	if stop > len(seq): stop = len(seq)

	start -= 1
	if start < 0: start = 0
	if start > stop:
		raise ValueError('stop must be <= stop')
	seq = seq.upper()
	numFullCodons = (stop - start) / 3
	aminoAcids = []
	for x in xrange(start, start + numFullCodons * 3, 3):
		if seq[x:x+3] in transTab1L:
			aminoAcids.append(transTab1L[seq[x:x+3]])
		else: aminoAcids.append('X')
	return ''.join(aminoAcids)



#def complement(strand):
#    comp = ''
#    for base in strand.upper():
#        comp = comp.join(TRANS[base])
#    yield TRANS[base]

geneDict = {}
ORFdict = {}
#firstLine = True
contigName = ''
head = []
headcount = 0

for line in mgFile:
    #print "hello world"
    while(line.startswith("#")):
        #headcount += 1
        if len(head) > 2:
            head = []
        head.append(line[2:])
        #continue
        #if headcount == 1:
            #contigName = line[2:]
        line = mgFile.next()
    
    #if contigName != str(head[0]):
    contigName = str(head[0]).strip()
    
    #print contigName
    linecount = 0
    line = line.split()
    name = line[0]
    start = line[1]
    stop = line[2]
    strand = line[3]
    frame = line[4]
    
    if line[6] > 0:
        #predicted gene
        if contigName in geneDict.keys():
            geneDict[contigName].append([name,start,stop,strand,frame])
        else:
            geneDict[contigName]=[[name,start,stop,strand,frame]]

    else:
        #predicted ORF
        if contigName in ORFdict.keys():
            ORFdict[contigName].append([name,start,stop,strand,frame])
        else:
            ORFdict[contigName]=[[name,start,stop,strand,frame]]

#print geneDict
#lastLine = ''
#
# for line, next_lines in get_next(mgFile):
#     #window size of two; check that current line and next two lines start with '#' this means were on contig name
#     if next_lines and next_lines.startswith("#") and line.startswith('#'): #and not (lastLine.startswith("#"):
#         contigName = line.strip("#").strip()
#         #print "contig name:", contigName
#         #print "next line:", next_lines
#     elif not line.startswith("#"):
#         #print "in else"
#         #print "line:", line
#         line = line.split()
#         name = line[0]
#         start = line[1]
#         stop = line[2]
#         strand = line[3]
#         frame = line[4]
#         
#         if line[6] > 0:
#             #predicted gene
#             if contigName in geneDict.keys():
#                 geneDict[contigName].append([name,start,stop,strand,frame])
#             else:
#                 geneDict[contigName]=[[name,start,stop,strand,frame]]
# 
#         else:
#             #predicted ORF
#             if contigName in ORFdict.keys():
#                 ORFdict[contigName].append([name,start,stop,strand,frame])
#             else:
#                 ORFdict[contigName]=[[name,start,stop,strand,frame]]
# 
#     #lastLine = line
# 
#     else:
#         continue

print "ORFs: ", len(ORFdict.keys())
print "Genes: ", len(geneDict.keys())

for header, seq in get_next_fasta(infasta):
    ORF = False
    
    try:
        geneList = geneDict[header[1:]]    
    except KeyError:
        try:
            geneList = ORFdict[header[1:]]
            ORF = True
        except KeyError:
            print header[1:], "nothing predicted!!"
            continue
        
    for gene in geneList:
        name = gene[0]
        start =int(gene[1])
        stop = int(gene[2])
        strand = gene[3]
        frame = int(gene[4])
        
        start = start+frame
        
        seqslice = seq[start-1:stop]
        #print start, stop
        #print seq

        if strand == '-':            
            seqslice = seqslice[::-1]
            seqslice = complementary_strand(seqslice)
        
            
        protseq = translateDNA(seqslice)
        
        if ORF is False:
            geneFasta.write("%s_%s\n%s\n" %(header, name, protseq) )
            nucfasta.write("%s_%s\n%s\n" %(header, name, seqslice) )
        else:
            ORFfasta.write("%s_%s\n%s\n" %(header, name, protseq) )

