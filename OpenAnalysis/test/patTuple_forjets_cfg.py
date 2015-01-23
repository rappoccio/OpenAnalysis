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


# Use the right global tag
process.GlobalTag.globaltag = cms.string( 'GR_R_42_V24::All' )

# require scraping filter
process.scrapingVeto = cms.EDFilter("FilterOutScraping",
                                    applyfilter = cms.untracked.bool(True),
                                    debugOn = cms.untracked.bool(False),
                                    numtrack = cms.untracked.uint32(10),
                                    thresh = cms.untracked.double(0.2)
                                    )
# HB + HE noise filtering
process.load('CommonTools/RecoAlgos/HBHENoiseFilter_cfi')
# Modify defaults setting to avoid an over-efficiency in the presence of OFT PU
process.HBHENoiseFilter.minIsolatedNoiseSumE = cms.double(999999.)
process.HBHENoiseFilter.minNumIsolatedNoiseChannels = cms.int32(999999)
process.HBHENoiseFilter.minIsolatedNoiseSumEt = cms.double(999999.)

###############################
####### DAF PV's     ##########
###############################

pvSrc = 'offlinePrimaryVertices'

process.primaryVertexFilter = cms.EDFilter("GoodVertexFilter",
                                           vertexCollection = cms.InputTag("goodOfflinePrimaryVertices"),
                                           minimumNDOF = cms.uint32(3) , # this is > 3
                                           maxAbsZ = cms.double(24), 
                                           maxd0 = cms.double(2) 
                                           )




from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( maxZ = cms.double(24.0),
                                     minNdof = cms.double(4.0) # this is >= 4
                                     ),
    src=cms.InputTag(pvSrc)
    )



# Generator-level jets (MC only, of course)
process.load("RecoJets.Configuration.GenJetParticles_cff")
from RecoJets.JetProducers.ak5PFJets_cfi import ak5PFJets
from RecoJets.JetProducers.ak5GenJets_cfi import ak5GenJets

process.ak5GenJetsNoNu = ak5GenJets.clone( rParam = cms.double(0.5),
                                           src = cms.InputTag("genParticlesForJetsNoNu"))
process.ak8GenJetsNoNu = ak5GenJets.clone( rParam = cms.double(0.8),
                                           src = cms.InputTag("genParticlesForJetsNoNu"))

process.ak8PFJets = ak5PFJets.clone(
    rParam = cms.double(0.8)
    )


addJetCollection(process, 
                 cms.InputTag('ak8PFJets'),
                 'AK8', 'PF',
                 doJTA=False,
                 doBTagging=False,
                 jetCorrLabel=('AK7PF', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual'])),
                 doType1MET=False,
                 doL1Cleaning=False,
                 doL1Counters=False,
                 genJetCollection = cms.InputTag("ak8GenJetsNoNu"),
                 doJetID = False
                 )


switchJetCollection(process,cms.InputTag('ak5PFJets'),
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual'])),
                 doType1MET   = True,
                 genJetCollection=cms.InputTag("ak5GenJetsNoNu"),
                 doJetID      = True
                 )


# Get the right level-1 (pileup) jet corrections
process.patJetCorrFactors.rho = cms.InputTag("kt6PFJets", "rho")
process.patJetCorrFactorsAK8PF.rho = cms.InputTag("kt6PFJets", "rho")
process.patJetCorrFactors.primaryVertices = "goodOfflinePrimaryVertices"
process.patJetCorrFactorsAK8PF.primaryVertices = "goodOfflinePrimaryVertices"


# run the trigger on the fly
process.load('PhysicsTools.PatAlgos.triggerLayer1.triggerProducer_cff')



# Select only triggers we want, write them out, and their prescales

mytrigs = [
        'HLT_Jet30U*',
        'HLT_Jet50U*',
        'HLT_Jet70U*',
        'HLT_Jet100U*'
    ]
from HLTrigger.HLTfilters.hltHighLevel_cfi import *
process.hltSelection1 = hltHighLevel.clone(TriggerResultsTag = 'TriggerResults::HLT', HLTPaths = mytrigs)
process.hltSelection1.throw = False
process.hltSelection = cms.Sequence( process.hltSelection1 )

process.dijetTriggerFilter = cms.EDFilter(
    "EDDijetTriggerFilter",
    src = cms.InputTag("patTriggerEvent"),
    trigs = cms.vstring( [
        'HLT_Jet30U',
        'HLT_Jet50U',
        'HLT_Jet70U',
        'HLT_Jet100U'
        ])
    )



process.npv = cms.EDFilter("VertexCountFilter",
                           src = cms.InputTag("goodOfflinePrimaryVertices")
                           )
                           
process.pvCount = cms.EDFilter("EDPileupAna",
                               src = cms.InputTag("goodOfflinePrimaryVertices")
                               )
                               

# Write out the ntuples of the jets and other relevant info
process.pfLite = cms.EDProducer(
    "CandViewNtpProducer", 
    src = cms.InputTag("particleFlow", "", "RECO"),
    lazyParser = cms.untracked.bool(True),
    prefix = cms.untracked.string(""),
    eventInfo = cms.untracked.bool(False),
    variables = cms.VPSet(
        cms.PSet(
            tag = cms.untracked.string("px"),
            quantity = cms.untracked.string("px()")
            ),
        cms.PSet(
            tag = cms.untracked.string("py"),
            quantity = cms.untracked.string("py()")
            ),
        cms.PSet(
            tag = cms.untracked.string("pz"),
            quantity = cms.untracked.string("pz()")
            ),
        cms.PSet(
            tag = cms.untracked.string("energy"),
            quantity = cms.untracked.string("energy()")
            ),
        cms.PSet(
            tag = cms.untracked.string("pdgId"),
            quantity = cms.untracked.string("pdgId()")
            )
        )  
    )



process.ak5Lite = cms.EDProducer(
    "CandViewNtpProducer", 
    src = cms.InputTag("selectedPatJets"),
    lazyParser = cms.untracked.bool(True),
    prefix = cms.untracked.string(""),
    eventInfo = cms.untracked.bool(False),
    variables = cms.VPSet(
        cms.PSet(
            tag = cms.untracked.string("px"),
            quantity = cms.untracked.string("px()")
            ),
        cms.PSet(
            tag = cms.untracked.string("py"),
            quantity = cms.untracked.string("py()")
            ),
        cms.PSet(
            tag = cms.untracked.string("pz"),
            quantity = cms.untracked.string("pz()")
            ),
        cms.PSet(
            tag = cms.untracked.string("energy"),
            quantity = cms.untracked.string("energy()")
            ),
        cms.PSet(
            tag = cms.untracked.string("jecFactor"),
            quantity = cms.untracked.string("jecFactor(0)")
            ),
        cms.PSet(
            tag = cms.untracked.string("jetArea"),
            quantity = cms.untracked.string("jetArea()")
            ),
        )  
    )


process.ak5GenLite = cms.EDProducer(
    "CandViewNtpProducer", 
    src = cms.InputTag("ak5GenJetsNoNu"),
    lazyParser = cms.untracked.bool(True),
    prefix = cms.untracked.string(""),
    eventInfo = cms.untracked.bool(False),
    variables = cms.VPSet(
        cms.PSet(
            tag = cms.untracked.string("px"),
            quantity = cms.untracked.string("px()")
            ),
        cms.PSet(
            tag = cms.untracked.string("py"),
            quantity = cms.untracked.string("py()")
            ),
        cms.PSet(
            tag = cms.untracked.string("pz"),
            quantity = cms.untracked.string("pz()")
            ),
        cms.PSet(
            tag = cms.untracked.string("energy"),
            quantity = cms.untracked.string("energy()")
            ),
        cms.PSet(
            tag = cms.untracked.string("jetArea"),
            quantity = cms.untracked.string("jetArea()")
            ),
        )  
    )

process.ak8Lite = process.ak5Lite.clone(
    src = cms.InputTag("selectedPatJetsAK8PF")
    )

process.ak8GenLite = process.ak5GenLite.clone(
    src = cms.InputTag("ak8GenJetsNoNu")
    )



## let it run
process.p = cms.Path(
    process.hltSelection*
    process.scrapingVeto*
    process.HBHENoiseFilter*
    process.goodOfflinePrimaryVertices*
    process.primaryVertexFilter*
    process.pvCount*
    process.ak8PFJets*
    process.patDefaultSequence*
    process.patTriggerDefaultSequence*
    process.dijetTriggerFilter*
    process.ak5Lite*
    process.ak8Lite*
    process.pfLite
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
process.maxEvents.input = 1000              ##  (e.g. -1 to run on all events)
#                                         ##

process.out.outputCommands = [
    'keep double_kt6PFJets_rho_*',
    'keep *_pvCount_*_*',
    'keep *_*Lite*_*_PAT',
    'keep *_dijetTriggerFilter_*_*',
                               ]
#   process.out.outputCommands = [ ... ]  ##  (e.g. taken from PhysicsTools/PatAlgos/python/patEventContent_cff.py)
#                                         ##
#   process.out.fileName = ...            ##  (e.g. 'myTuple.root')
#                                         ##
process.options.wantSummary = True       ##  (to suppress the long output at the end of the job)    

