#ifndef __SIMPLEDET_EDEPSIM_EDEPSIMINTERFACE_H__
#define __SIMPLEDET_EDEPSIM_EDEPSIMINTERFACE_H__

#include <Python.h>
#include "bytesobject.h"

#include <vector>
#include <set>
#include <map>

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
				  int offset_x_pixels, int offset_y_pixels,
				  float threshold, int rand_pix_from_center );

    std::vector<int> getPixelIndices( float x, float y ) const;
    
    int padding[2];
    float pixelsize[2];
    int npixels[2];

    float origin[2];
    float planelen[2];
    float max_gridpt[2];
    
    float max_step_size;
    float distance_to_readout_plane;


    struct PixInfo_t {
      unsigned long pixid;
      unsigned long indices[3];
      unsigned long container_index;
      long trackid;
      float edep;
      PixInfo_t() {
	pixid = 4294967294;
      };
      bool operator<( const PixInfo_t& rhs ) const {
	if ( pixid<rhs.pixid )
	  return true;
	return false;
      };
    };

    struct EDepInfo_t {
      long trackid;
      unsigned long pixid;      
      mutable float edep_sum;
      EDepInfo_t()
	: trackid(0),
	  pixid(0),
	  edep_sum(0.0)
      {};
      EDepInfo_t( long tid )
	: trackid(tid),
	  pixid(0),
	  edep_sum(0.0)
      {};
      bool operator<( const EDepInfo_t& rhs ) const {
	if ( trackid < rhs.trackid )
	  return true;
	return false;
      };
      // bool operator==( const EDepInfo_t& rhs ) const {
      // 	if ( trackid==rhs.trackid ) return true;
      // 	return false;
      // };
    };

  protected:
    
    std::map< unsigned long, PixInfo_t > _pixinfo_map;
    std::vector< std::set<EDepInfo_t> >  _edep_map;

    
  private:

    static bool __loaded_numpy;

  };
  
}
}
 

#endif
