import ROOT

ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

from DataFormats.FWLite import Events, Handle

############################################
#     Trigger information                  #
############################################
# Use the same trigger thresholds as QCD-11-004 in AN-364-v4 Table 8

class TrigHelper :
    def __init__ ( self, checkNames=False, verbose=False ) :
        self.checkNames = checkNames
        self.verbose=verbose
        self.trigLabel = ( "dijetTriggerFilter", 'jetPaths')
        self.trigHandle = Handle("std::vector<std::string>")
        self.trigPrescaleLabel = ( "dijetTriggerFilter", 'prescales')
        self.trigPrescaleHandle = Handle("std::vector<int>")
        # Here are the trigger thresholds for the various eta bins.
        # In the following, each entry is an eta bin. The
        # two fields are then [etamin,etamax], and the
        self.trigThresholds = [ 56., 84., 114., 153., 196.,  7000.]
        self.trigsToKeep = [
            'HLT_Jet30U',
            'HLT_Jet50U',
            'HLT_Jet70U',
            'HLT_Jet100U'
        ]

    def passEventMC( self, event, ptMax ) :

        for ibin in range(0, len(self.trigThresholds)) :
            if ptMax >= self.trigThresholds[ibin] and ptMax < self.trigThresholds[ibin+1] :
                return True

    def passEventData( self, event, ptMax ) :
        iTrigHist = None
        event.getByLabel( self.trigLabel, self.trigHandle )
        trigs = self.trigHandle.product()
        event.getByLabel( self.trigPrescaleLabel, self.trigPrescaleHandle )
        prescales = self.trigPrescaleHandle.product()

        acceptedPaths = []
        trigPassedName = None
        passPtMaxTrig = False
        finalPrescale = None

        # If there are any accepted paths, cache them. Then match to the lookup table "trigThresholds" to see if
        # the event is in the correct mjj bin for the trigger in question.
        if len( trigs ) > 0 :
            for ipath in xrange( len(trigs)-1, -1, -1) :
                path = trigs[ipath]
                prescale = prescales[ipath]
                for ikeep in xrange(len(self.trigsToKeep)-1, -1, -1) :
                    if self.verbose :
                        print '   ----- checking trigger ' + self.trigsToKeep[ikeep] + ' : ptMaxThreshold = ' + str(self.trigThresholds[ikeep])
                    if path.find( self.trigsToKeep[ikeep] ) >= 0 and ptMax >= self.trigThresholds[ikeep] and ptMax < self.trigThresholds[ikeep + 1]:
                        trigPassedName = path
                        iTrigHist = ikeep
                        finalPrescale = prescale
                        passPtMaxTrig = True
                        if self.verbose :
                            print '    -----------> Joy and elation, it worked! trigger = ' + self.trigsToKeep[iTrigHist]
                        break
                if passPtMaxTrig == True :
                    break

        passEvent = passPtMaxTrig
        return [passEvent,iTrigHist,finalPrescale]
