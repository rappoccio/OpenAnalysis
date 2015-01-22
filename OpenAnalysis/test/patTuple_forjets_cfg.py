## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

from PhysicsTools.PatAlgos.tools.coreTools import *
removeMCMatching(process, ['All'])

## uncomment the following line to add tcMET to the event content
from PhysicsTools.PatAlgos.tools.metTools import *
addPfMET(process, 'PF')

## uncomment the following line to add different jet collections
## to the event content
from PhysicsTools.PatAlgos.tools.jetTools import *

## uncomment the following lines to add ak5JPTJets to your PAT output
## addJetCollection(process,cms.InputTag('JetPlusTrackZSPCorJetAntiKt5'),
##                  'AK5', 'JPT',
##                  doJTA        = True,
##                  doBTagging   = True,
##                  jetCorrLabel = ('AK5JPT', cms.vstring(['L1Offset', 'L1JPTOffset', 'L2Relative', 'L3Absolute'])),
##                  doType1MET   = False,
##                  doL1Cleaning = False,
##                  doL1Counters = True,                 
##                  genJetCollection = cms.InputTag("ak5GenJets"),
##                  doJetID      = True,
##                  jetIdLabel   = "ak5"
##                  )

## uncomment the following lines to add ak7CaloJets to your PAT output

## uncomment the following lines to add ak5PFJets to your PAT output
switchJetCollection(process,cms.InputTag('ak5PFJets'),
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute'])),
                 doType1MET   = True,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True
                 )

## let it run
process.p = cms.Path(
    process.patDefaultSequence
)



## ------------------------------------------------------
#  In addition you usually want to change the following
#  parameters:
## ------------------------------------------------------
#
#   process.GlobalTag.globaltag =  ...    ##  (according to https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideFrontierConditions)
#                                         ##
process.source.fileNames = [          ##
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/00995B6D-8B71-E011-A82A-003048D439C6.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/00D36368-A371-E011-907D-003048D3CD62.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/025B6369-F670-E011-A4FF-00215AD4D6C8.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/027648DA-9371-E011-9BB7-0025901D4D76.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/06DF8C41-3571-E011-8F8B-002481E0DE14.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0A3DAC87-5471-E011-9FDC-003048C662D4.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0AC6E23E-B071-E011-B806-003048D47776.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0AE833E2-EF70-E011-8F8E-003048D43996.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0AF5FD68-F670-E011-8687-002481E0D69C.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0C401619-9A71-E011-8FF2-003048C69314.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0E2AA93A-8B71-E011-A4CC-0025901D4B02.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0E4D379B-3871-E011-A4DB-003048D43982.root',
'root://eospublic.cern.ch//eos/opendata/cms/Run2010B/Jet/AOD/Apr21ReReco-v1/0004/0E87E892-1E71-E011-83E8-003048C693F2.root'
]                                     ##  (e.g. 'file:AOD.root')
#                                         ##
process.maxEvents.input = 10              ##  (e.g. -1 to run on all events)
#                                         ##
#   process.out.outputCommands = [ ... ]  ##  (e.g. taken from PhysicsTools/PatAlgos/python/patEventContent_cff.py)
#                                         ##
#   process.out.fileName = ...            ##  (e.g. 'myTuple.root')
#                                         ##
process.options.wantSummary = False       ##  (to suppress the long output at the end of the job)    

