#ifndef __SIMPLEDET_EDEPSIM_EDEPSIMINTERFACE_H__
#define __SIMPLEDET_EDEPSIM_EDEPSIMINTERFACE_H__

#include <Python.h>
#include "bytesobject.h"

#include <vector>

#include "EDepSim/TG4HitSegment.h"
#include "TH2D.h"

namespace simpledet {
namespace edepsim {

  class EDepSimInterface {
  public:

    EDepSimInterface();
    virtual ~EDepSimInterface() {};

    std::vector<float> processSegmentHits( const TG4HitSegmentContainer& hit_container );
    TH2D* makeWholeDetectorTH2D( const TG4HitSegmentContainer& hit_container );
    PyObject* makeNumpyArrayCrop( const TG4HitSegmentContainer& hit_container, int img_pixdim,
				  int offset_x_pixels, int offset_y_pixels, int rand_pix_from_center );
    
    int padding[2];
    float pixelsize[2];
    int npixels[2];

    float origin[2];
    float planelen[2];
    float max_gridpt[2];
    
    float max_step_size;

  private:

    static bool __loaded_numpy;

  };
  
}
}
 

#endif
