#ifndef __SIMPLEDET_EDEPSIM_EDEPSIMINTERFACE_H__
#define __SIMPLEDET_EDEPSIM_EDEPSIMINTERFACE_H__

#include "EDepSim/TG4HitSegment.h"
#include "TH2D.h"

namespace simpledet {
namespace edepsim {

  class EDepSimInterface {
  public:

    EDepSimInterface() {};
    virtual ~EDepSimInterface() {};

    TH2D processSegmentHits( const TG4HitSegmentContainer& hit_container );

  };
  
}
}
 

#endif
