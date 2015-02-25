#!/usr/bin/env python
# Ripped and adapted from http://wlav.web.cern.ch/wlav/pyroot/tpytree.html

import ROOT

# Workaround the framework's Wrapper class so pyroot can handle it. 
#ROOT.gROOT.LoadMacro( 'Wrapper.C')
ROOT.gInterpreter.GenerateDictionary("edm::Wrapper<vector<int> >","Wrapper.h")
ROOT.gInterpreter.GenerateDictionary("edm::Wrapper<vector<float> >","Wrapper.h")
ROOT.gInterpreter.GenerateDictionary("edm::Wrapper<vector<string> >","Wrapper.h")


# Help out with the trigger prescales
from TrigHelperBare import TrigHelper


# open the file
myfile = ROOT.TFile( '/data/Public/2010/Jet/patTuple.root' )

# retrieve the ntuple of interest
tree = myfile.Get( 'Events' )
entries = tree.GetEntries()

# Get the AK8 jets
ak8Lite_px = ROOT.edm.Wrapper('vector<float>')()
ak8Lite_py = ROOT.edm.Wrapper('vector<float>')()
ak8Lite_pz = ROOT.edm.Wrapper('vector<float>')()
ak8Lite_energy = ROOT.edm.Wrapper('vector<float>')()

# Get the prescales
prescales = ROOT.edm.Wrapper('vector<int>')()
trigs = ROOT.edm.Wrapper('vector<string>')()


# Turn off all branches but the ones we want

tree.SetBranchAddress('floats_ak8Lite_px_PAT.', ak8Lite_px)
tree.SetBranchAddress('floats_ak8Lite_py_PAT.', ak8Lite_py)
tree.SetBranchAddress('floats_ak8Lite_pz_PAT.', ak8Lite_pz)
tree.SetBranchAddress('floats_ak8Lite_energy_PAT.', ak8Lite_energy)
tree.SetBranchAddress('ints_dijetTriggerFilter_prescales_PAT.', prescales )


# Instantiate the trigger helper
trigHelper = TrigHelper( prescales.obj )


# get a file to write hists to
f = ROOT.TFile("outplots.root", "RECREATE")

# Make histograms
h_pt0 = ROOT.TH1F("h_pt0", "Leading Jet p_{T};p_{T} (GeV);Number", 50, 0, 500)

# Loop over events
for jentry in xrange( entries ):

    if jentry %1000 == 0 :
        print jentry

    # copy next entry into memory and verify
    nb = tree.GetEntry( jentry )
    if nb <= 0:
        continue


    # Get the list of jets, and maximum pt to decide
    # which trigger bin this should be in. 
    ptMax = -1.0
    goodJets = []
    for ipf in xrange( ak8Lite_px.obj.size() ) :
        v = ROOT.TLorentzVector( ak8Lite_px.obj[ipf],
                                 ak8Lite_py.obj[ipf],
                                 ak8Lite_pz.obj[ipf],
                                 ak8Lite_energy.obj[ipf] )
        if v.Perp() > 30.0 and abs(v.Eta()) < 2.4 :
            goodJets.append( v )
            
        if v.Perp() > ptMax :
            ptMax = v.Perp()


    if ptMax < 0 :
        continue
            
    [passEvent,iTrigHist,prescale] = trigHelper.passEventData(ptMax )

    if not passEvent :
        continue

    if len(goodJets) < 1 :
        continue
    weight = prescale

    h_pt0.Fill( goodJets[0].Perp(), weight )



f.cd()
f.Write()
