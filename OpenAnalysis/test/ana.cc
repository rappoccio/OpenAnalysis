#include <memory>
#include <string>
#include <vector>
#include <sstream>
#include <fstream>
#include <iostream>

#include <TH1F.h>
#include <TROOT.h>
#include <TFile.h>
#include <TSystem.h>
#include <TLorentzVector.h>

#include "DataFormats/FWLite/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"

#include <fastjet/PseudoJet.hh>
#include <fastjet/ClusterSequenceArea.hh>

int main(int argc, char* argv[]) 
{
  // ----------------------------------------------------------------------
  //  * enable the AutoLibraryLoader 
  //  * book the histograms of interest 
  //  * open the input file
  // ----------------------------------------------------------------------

  // load framework libraries
  gSystem->Load( "libFWCoreFWLite" );
  AutoLibraryLoader::enable();

  // ----------------------------------------------------------------------
  // Create the JetCorrectorParameter objects, the order does not matter.
  // ----------------------------------------------------------------------
  std::cout << "Setting up JetCorrectorParameters." << std::endl;
  std::cout << "L2L3 res:" << std::endl;
  JetCorrectorParameters ResJetPar ("JECFiles/GR_R_42_V24_AK5PF_L2L3Residual.txt"); 
  std::cout << "L3 res:" << std::endl;
  JetCorrectorParameters L3JetPar  ("JECFiles/GR_R_42_V24_AK5PF_L3Absolute.txt");
  std::cout << "L2 res:" << std::endl;
  JetCorrectorParameters L2JetPar  ("JECFiles/GR_R_42_V24_AK5PF_L2Relative.txt");
  std::cout << "L1 res:" << std::endl;
  JetCorrectorParameters L1JetPar  ("JECFiles/GR_R_42_V24_AK5PF_L1FastJet.txt");
  std::cout << "done with JetCorrectorParameters" << std::endl;
  // ----------------------------------------------------------------------
  //  Load the JetCorrectorParameter objects into a vector, IMPORTANT: THE ORDER MATTERS HERE !!!! 
  // ----------------------------------------------------------------------
  std::vector<JetCorrectorParameters> vPar;
  vPar.push_back(L1JetPar);
  vPar.push_back(L2JetPar);
  vPar.push_back(L3JetPar);
  vPar.push_back(ResJetPar);
  
  std::cout << "Setting up FactorizedJetCorrector" << std::endl;
  FactorizedJetCorrector *jetCorrector = new FactorizedJetCorrector(vPar);
  
  std::cout << "Done, about to get inputs." << std::endl;

  int maxEvents_ = 10;
  std::string outputFile_ = "anatest.root";
  std::vector<std::string> inputFiles_;
  inputFiles_.push_back("patTuple.root");

  bool verbose = false;

  // ----------------------------------------------------------------------
  // book a set of histograms
  // ----------------------------------------------------------------------
  fwlite::TFileService fs = fwlite::TFileService(outputFile_.c_str());
  TFileDirectory dir = fs.mkdir("ana");
  TH1F* h_pt_  = dir.make<TH1F>("pt"  , "pt"  ,   100,   0., 300.);
  

  // ----------------------------------------------------------------------
  std::cout << "About to loop" << std::endl;
  // loop the events
  // ----------------------------------------------------------------------
  int ievt=0;  
  for(unsigned int iFile=0; iFile<inputFiles_.size(); ++iFile){

    TFile* inFile = TFile::Open(inputFiles_[iFile].c_str());
    if( inFile ){
      fwlite::Event ev(inFile);
      for(ev.toBegin(); !ev.atEnd(); ++ev, ++ievt){

	if ( verbose ) 
	  std::cout << "=====================" << std::endl;

	edm::EventBase const & event = ev;

	// ----------------------------------------------------------------------
	// Access the data inside of the event with an "edm::Handle" (fancy pointer to the collection). 
	// Then get the object you're interested in. 
	// ----------------------------------------------------------------------


	// ----------------------------------------------------------------------
	// Trigger stuff
	// ----------------------------------------------------------------------
	// Trigger names and prescales
	edm::Handle< std::vector<int> > trigPrescalesHandle;	
	event.getByLabel( edm::InputTag("dijetTriggerFilter", "prescales"), trigPrescalesHandle );
	edm::Handle< std::vector<std::string> > trigNamesHandle;
	event.getByLabel( edm::InputTag("dijetTriggerFilter", "jetPaths"), trigNamesHandle );

	// Get the triggers that fired and their prescales. 
	bool foundJet30U = false; float prescaleJet30U = 1;
	bool foundJet50U = false; float prescaleJet50U = 1;
	bool foundJet70U = false; float prescaleJet70U = 1;
	bool foundJet100U = false; float prescaleJet100U = 1;
	
	// Jet30U
	std::vector<std::string>::const_iterator jet30U = find( trigNamesHandle->begin(), trigNamesHandle->end(), "HLT_Jet30U" );
	if ( jet30U != trigNamesHandle->end() ) {
	  foundJet30U = true; prescaleJet30U = trigPrescalesHandle->at( jet30U - trigNamesHandle->begin() );
	}

	// Jet50U
	std::vector<std::string>::const_iterator jet50U = find( trigNamesHandle->begin(), trigNamesHandle->end(), "HLT_Jet50U" );
	if ( jet50U != trigNamesHandle->end() ) {
	  foundJet50U = true; prescaleJet50U = trigPrescalesHandle->at( jet50U - trigNamesHandle->begin() );
	}

	// Jet70U
	std::vector<std::string>::const_iterator jet70U = find( trigNamesHandle->begin(), trigNamesHandle->end(), "HLT_Jet70U" );
	if ( jet70U != trigNamesHandle->end() ) {
	  foundJet70U = true; prescaleJet70U = trigPrescalesHandle->at( jet70U - trigNamesHandle->begin() );
	}

	// Jet100U
	std::vector<std::string>::const_iterator jet100U = find( trigNamesHandle->begin(), trigNamesHandle->end(), "HLT_Jet100U" );
	if ( jet100U != trigNamesHandle->end() ) {
	  foundJet100U = true; prescaleJet100U = trigPrescalesHandle->at( jet100U - trigNamesHandle->begin() );
	}
	if ( verbose ) {
	  std::cout << "Jet30U : " << foundJet30U << ", prescale = " << prescaleJet30U << std::endl;
	  std::cout << "Jet50U : " << foundJet50U << ", prescale = " << prescaleJet50U << std::endl;
	  std::cout << "Jet70U : " << foundJet70U << ", prescale = " << prescaleJet70U << std::endl;
	  std::cout << "Jet100U: " << foundJet100U<< ", prescale = " << prescaleJet100U<< std::endl;
	}

	// ----------------------------------------------------------------------
	// Jets and PF stuff
	// ----------------------------------------------------------------------

	// Median pt per unit area.
	edm::Handle<double> rhoHandle;
	event.getByLabel( edm::InputTag("kt6PFJets", "rho"), rhoHandle);
	double rho = (*rhoHandle);

	// AK5 jets from the event
	edm::Handle<std::vector<float> > ak5_pxs;
	edm::Handle<std::vector<float> > ak5_pys;
	edm::Handle<std::vector<float> > ak5_pzs;
	edm::Handle<std::vector<float> > ak5_energies;
	event.getByLabel( edm::InputTag("ak5Lite", "px"), ak5_pxs);
	event.getByLabel( edm::InputTag("ak5Lite", "py"), ak5_pys);
	event.getByLabel( edm::InputTag("ak5Lite", "pz"), ak5_pzs);
	event.getByLabel( edm::InputTag("ak5Lite", "energy"), ak5_energies);

	// Loop and print
	if ( verbose ) {
	  for ( unsigned int ijet = 0; ijet < ak5_pxs->size(); ++ijet ) {
	    char buff[1000];
	    TLorentzVector p4_jet( ak5_pxs->at(ijet), ak5_pys->at(ijet), ak5_pzs->at(ijet), ak5_energies->at(ijet) );
	    sprintf( buff, "%6d : pt = %6.2f, eta = %6.2f, phi = %6.2f, m = %6.2f", ijet, p4_jet.Perp(), p4_jet.Rapidity(), p4_jet.Phi(), p4_jet.M() );
	    std::cout << buff << std::endl;
	  }
	}

	// PF candidates from the event
	edm::Handle<std::vector<float> > pf_pxs;
	edm::Handle<std::vector<float> > pf_pys;
	edm::Handle<std::vector<float> > pf_pzs;
	edm::Handle<std::vector<float> > pf_energies;
	edm::Handle<std::vector<float> > pf_pdgids;

	event.getByLabel( edm::InputTag("pfLite", "px"), pf_pxs);
	event.getByLabel( edm::InputTag("pfLite", "py"), pf_pys);
	event.getByLabel( edm::InputTag("pfLite", "pz"), pf_pzs);
	event.getByLabel( edm::InputTag("pfLite", "energy"), pf_energies);
	event.getByLabel( edm::InputTag("pfLite", "pdgId"), pf_pdgids);

	// Loop and print
	std::vector<fastjet::PseudoJet> inputs;
	for ( unsigned int ipf = 0; ipf < pf_pxs->size(); ++ipf ) {
	  fastjet::PseudoJet input( pf_pxs->at(ipf), pf_pys->at(ipf), pf_pzs->at(ipf), pf_energies->at(ipf) );
	  inputs.push_back( input );
	}


	// ----------------------------------------------------------------------
	// Recluster the jets
	// ----------------------------------------------------------------------
	double R = 0.5;
	fastjet::JetDefinition jet_def(fastjet::antikt_algorithm, R);
	double maxrap = 5.0;
	unsigned int n_repeat = 1; // default is 1
	double ghost_area = 0.01; // this is the default
	fastjet::GhostedAreaSpec area_spec(maxrap, n_repeat, ghost_area);	
	fastjet::AreaDefinition area_def(fastjet::active_area, area_spec);
	fastjet::ClusterSequenceArea clust_seq(inputs, jet_def, area_def);
	
	
	// ----------------------------------------------------------------------
	// get the resulting jets ordered in pt
	// ----------------------------------------------------------------------
	double ptmin = 3.0;
	std::vector<fastjet::PseudoJet> inclusive_jets = clust_seq.inclusive_jets(ptmin);

	// ----------------------------------------------------------------------
	// Correct the jets with latest JEC's
	// ----------------------------------------------------------------------

	for ( unsigned int ijet = 0; ijet < inclusive_jets.size(); ++ijet ) {
	  jetCorrector->setJetEta( inclusive_jets[ijet].eta() );
	  jetCorrector->setJetPt( inclusive_jets[ijet].perp() );
	  jetCorrector->setJetA( inclusive_jets[ijet].area()  );
	  jetCorrector->setRho(rho);
	  double corr = jetCorrector->getCorrection();

	  inclusive_jets[ijet] *= corr;
	}
	// Resort after JEC's
	inclusive_jets = sorted_by_pt( inclusive_jets );

	// Loop and print
	if ( verbose ) {
	  for ( unsigned int ijet = 0; ijet < inclusive_jets.size(); ++ijet ) {
	    char buff[1000];
	    sprintf( buff, "%6d : pt = %6.2f, eta = %6.2f, phi = %6.2f, m = %6.2f", ijet, 
		     inclusive_jets[ijet].perp(), 
		     inclusive_jets[ijet].rap(), 
		     inclusive_jets[ijet].phi(), 
		     inclusive_jets[ijet].m() );
	    std::cout << buff << std::endl;
	  }
	}
	
	// ----------------------------------------------------------------------
	// User-level trigger usage goes here. Here we base the decision on the
	// pt of the leading jet. There are other ways to do this if desired. 
	// ----------------------------------------------------------------------=
	if ( inclusive_jets.size() < 1 ) {
	  std::cout << "No jets. Skipping." << std::endl;
	  continue;
	}
	double ptMax = inclusive_jets[0].perp();
	bool passTrig = false;
	float prescale = 1.0;
	if ( foundJet100U && ptMax >= 196.0 ) {
	  passTrig = true;
	  prescale = prescaleJet100U;
	} else if ( foundJet70U && 153.0 <= ptMax && ptMax < 196. ) {
	  passTrig = true;
	  prescale = prescaleJet70U;
	} else if ( foundJet50U && 114.0 <= ptMax && ptMax < 153. ) {
	  passTrig = true;
	  prescale = prescaleJet50U;
	} else if ( foundJet30U && 84.0 <= ptMax && ptMax < 114. ) {
	  passTrig = true;
	  prescale = prescaleJet30U;
	} 

	if ( passTrig ) {
	  if ( verbose ) 
	    std::cout << "ptMax = " << ptMax << ", prescale = " << prescale << std::endl;
	  
	  // If you fill with "prescale", the histograms should come out properly "stitched". 
	  h_pt_->Fill( ptMax, prescale );

	}
      }
      // close input file
      inFile->Close();
    }
  }

  
  delete jetCorrector;
  return 0;
}
