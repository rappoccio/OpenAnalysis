#! /usr/bin/env python
import os
import glob
import math
from array import *

from optparse import OptionParser

parser = OptionParser()


############################################
#            Job steering                  #
############################################

# Input files to use. This is in "glob" format, so you can use wildcards.
# If you get a "cannot find file" type of error, be sure to use "\*" instead
# of "*" to make sure you don't confuse the shell. 
parser.add_option('--files', metavar='F', type='string', action='store',
		  dest='files',
                  help='Input files')

# Output name to use. 
parser.add_option('--outname', metavar='F', type='string', action='store',
                  default='anahists',
                  dest='outname',
                  help='output name')

# JEC systematics
parser.add_option('--jecUnc', type='int', action='store',
                  default=None,
                  dest='jecUnc',
                  help='Jet energy correction uncertainty: 1 for up, -1 for down, None for nominal')



# Print verbose information
parser.add_option('--verbose', action='store_true',
                  default=False,
                  dest='verbose',
                  help='Print verbose information')

# job splitting

parser.add_option('--max', type='int', action='store',
                  default=None,
                  dest='max',
                  help='Max number')
parser.add_option('--nsplit', type='int', action='store',
                  default=None,
                  dest='nsplit',
                  help='Number of split jobs')
parser.add_option('--isplit', type='int', action='store',
                  default=None,
                  dest='isplit',
		  help='Index of job (0...nsplit)')

(options, args) = parser.parse_args()

argv = []

# Import everything from ROOT
import ROOT
ROOT.gROOT.Macro("rootlogon.C")

# Import stuff from FWLite
import sys
from DataFormats.FWLite import Events, Handle

ROOT.gSystem.Load('libCondFormatsJetMETObjects')

from TrigHelper import TrigHelper

trigHelper = TrigHelper()



#############################
# Get the input files,
# and split them to increase
# processing speed. 
#############################

print 'Getting files from this dir: ' + options.files

files = []
# Get the file list.
if options.files.find('.txt') >= 0 :
    infile = open( options.files, 'r')
    tmpfiles = infile.readlines()
    for ifile in tmpfiles :
        s = ifile.rstrip()
        print s
        files.append( s )

elif options.nsplit is None :
    files = glob.glob( options.files )
    for ifile in files:
        print ifile
elif options.nsplit is not None :


    tmpfiles = glob.glob( options.files )
    print 'All files : '  + str(len(tmpfiles))
    for ifile in tmpfiles :
        print ifile

    tot = len(tmpfiles)
    nsplit = options.nsplit
    isplit = options.isplit
    msplit = tot / nsplit
    print 'Splitting into ' + str(nsplit) + ' jobs with ' + str(msplit) + ' elements each, this job is index ' + str(isplit)
    end = min( tot, (isplit + 1) * msplit )
    for i in range( isplit * msplit, end ) :
        files.append( tmpfiles[i] )
    print 'Selected files : '
    for ifile in files :
        print ifile

if len(files) == 0 :
    print 'No files, exiting'
    exit(0)

# Create the output file. 
f = ROOT.TFile(options.outname + ".root", "recreate")
f.cd()


# Make histograms
print "Creating histograms"

nJets = ROOT.TH1F("nJets",         "Number of Jets, p_{T} > 30 GeV;N_{Jets};Number",               20, -0.5, 19.5 )

h_pt   = ROOT.TH1F('h_pt', ';p_{T} (GeV);Number', 25, 0, 200)
h_y    = ROOT.TH1F('h_y', ';Rapidity;Number', 25, -5.0, 5.0)
h_phi  = ROOT.TH1F('h_phi', ';#phi (radians);Number', 25, 0, ROOT.TMath.TwoPi() )
h_m    = ROOT.TH1F('h_m', ';Mass (GeV);Number', 25, 0, 50)

############################################
#     Jet energy scale and uncertainties   #
############################################

jecStr = [
    'Jec11_V3_L1FastJet_AK5PFchs.txt',
    'Jec11_V3_L2Relative_AK5PFchs.txt',
    'Jec11_V3_L3Absolute_AK5PFchs.txt',
    'Jec11_V3_L2L3Residual_AK5PFchs.txt'
    ]
jecUncStr = ROOT.std.string('Jec11_V3_Uncertainty_AK5PFchs.txt')



#jecPars = ROOT.std.vector(ROOT.JetCorrectorParameters)()

#for ijecStr in jecStr :
#    ijec = ROOT.JetCorrectorParameters( ijecStr )
#    jecPars.push_back( ijec )
    

#jec = ROOT.FactorizedJetCorrector(jecPars)

#if options.jecUnc is not None:
#    jecUnc = ROOT.JetCorrectionUncertainty( jecUncStr )
#    upOrDown = options.jecUnc > 0.0
#else :
#    jecUnc = None
#    upOrDown = None



############################################
# Collection names, etc #
############################################

ak5PFJetsPxHandle = Handle( "std::vector<float>" )
ak5PFJetsPxLabel = ("ak5Lite", "px")
ak5PFJetsPyHandle = Handle( "std::vector<float>" )
ak5PFJetsPyLabel = ("ak5Lite", "py")
ak5PFJetsPzHandle = Handle( "std::vector<float>" )
ak5PFJetsPzLabel = ("ak5Lite", "pz")
ak5PFJetsEnergyHandle = Handle( "std::vector<float>" )
ak5PFJetsEnergyLabel = ("ak5Lite", "energy")



# Mean-pt-per-unit-area
rhoHandle = Handle("double")
rhoLabel = ( "kt6PFJets", "rho")

# Pileup information
puHandle = Handle("std::vector<PileupSummaryInfo>")
puLabel = ( "addPileupInfo", "")
npvHandle = Handle("double")
npvLabel = ( "pvCount", "npv")



count = 0

for ifile in files :

    events = Events (ifile)

    print "Start looping on file " + ifile

    if options.max is not None:
        if count > options.max :
            break

    for event in events:

        if options.max is not None:
            if count > options.max :
                break

        # Histogram filling weight
        weight = 1.0

        # Histogram index for data (Jet60,110,190,240,370)
        iTrigHist = None
        
        if count % 10000 == 0 or options.verbose :
            print '-------------------------------------------------  Processing event ' + str(count) + '--------------------------------------'


        count += 1

        
        # For printing and comparison
        mjetFinal = []

        event.getByLabel( rhoLabel, rhoHandle )
        rho = rhoHandle.product()[0]
        event.getByLabel( npvLabel, npvHandle )
        nvtx = npvHandle.product()[0]



        event.getByLabel( ak5PFJetsPxLabel, ak5PFJetsPxHandle )
        event.getByLabel( ak5PFJetsPyLabel, ak5PFJetsPyHandle )
        event.getByLabel( ak5PFJetsPzLabel, ak5PFJetsPzHandle )
        event.getByLabel( ak5PFJetsEnergyLabel, ak5PFJetsEnergyHandle )

        ak5Pxs = ak5PFJetsPxHandle.product()
        ak5Pys = ak5PFJetsPyHandle.product()
        ak5Pzs = ak5PFJetsPzHandle.product()
        ak5Energys = ak5PFJetsEnergyHandle.product()

        ptMax = -1.0
        jetMax = None

        for ijet in xrange( len( ak5Pxs) ) :
            ak5Px = ak5Pxs[ijet]
            ak5Py = ak5Pys[ijet]
            ak5Pz = ak5Pzs[ijet]
            ak5E  = ak5Energys[ijet]
            jet = ROOT.TLorentzVector( ak5Px, ak5Py, ak5Pz, ak5E )
            if jet.Perp() > ptMax :
                ptMax = jet.Perp()
                jetMax = jet

            if options.verbose : 
                print 'ijet = {0:6.0f} : pt={1:6.2f},y={2:6.2f},phi={3:6.2f},m={4:6.2f}'.format( ijet, jet.Perp(), jet.Rapidity(), jet.Phi(), jet.M() )



        [passEvent,iTrigHist,prescale] = trigHelper.passEventData(event, ptMax )

        if not passEvent :
            continue

        weight *= prescale

        h_pt.Fill( jetMax.Perp(), weight )
        h_y.Fill( jetMax.Rapidity(), weight )
        h_phi.Fill( jetMax.Phi(), weight )
        h_m.Fill( jetMax.M(), weight )

        if options.verbose :
            print 'event passed : index = {0:6.0f} prescale = {1:6.0f}, nvtx = {2:6.0f}, rho = {3:6.2f}'.format( iTrigHist, prescale, nvtx, rho  )


##         event.getByLabel( pfPxLabel, pfPxHandle )
##         event.getByLabel( pfPyLabel, pfPyHandle )
##         event.getByLabel( pfPzLabel, pfPzHandle )
##         event.getByLabel( pfEnergyLabel, pfEnergyHandle )

##         ak5Pxs = pfPxHandle.product()
##         ak5Pys = pfPyHandle.product()
##         ak5Pzs = pfPzHandle.product()
##         ak5Energys = pfEnergyHandle.product()        

##         for ijet in xrange( len( ak5Pxs) ) :
##             ak5Px = ak5Pxs[ijet]
##             ak5Py = ak5Pys[ijet]
##             ak5Pz = ak5Pzs[ijet]
##             ak5E  = ak5Energys[ijet]
##             jet = ROOT.TLorentzVector( ak5Px, ak5Py, ak5Pz, ak5E )

##             print 'ijet = {0:6.0f} : pt={1:6.2f},y={2:6.2f},phi={3:6.2f},m={4:6.2f}'.format( ijet, jet.Perp(), jet.Rapidity(), jet.Phi(), jet.Mass() )



            


f.cd()    
f.Write()

