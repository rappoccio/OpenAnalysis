import ROOT


############################################
#     Trigger information                  #
############################################
# Use the same trigger thresholds as QCD-11-004 in AN-364-v4 Table 8

class TrigHelper :
    def __init__ ( self, prescales, verbose=False ) :
        self.verbose=verbose
        self.prescales = prescales
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


    def passEventData( self, ptMax ) :
        iTrigHist = None

        acceptedPaths = []
        trigPassedName = None
        passPtMaxTrig = False
        finalPrescale = None

        # If there are any accepted paths, cache them. Then match to the lookup table "trigThresholds" to see if
        # the event is in the correct mjj bin for the trigger in question.
        if len( self.prescales ) > 0 :
            for ipath in xrange( len(self.prescales)-1, -1, -1) :
                prescale = self.prescales[ipath]
                for ikeep in xrange(len(self.trigThresholds)-1, -1, -1) :
                    if prescale >= 0 and ptMax >= self.trigThresholds[ikeep] and ptMax < self.trigThresholds[ikeep + 1]:
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
