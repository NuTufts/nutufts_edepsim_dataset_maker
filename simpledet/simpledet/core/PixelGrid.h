#ifndef __SIMPLEDET_CORE_PIXELGRID_H__
#define __SIMPLEDET_CORE_PIXELGRID_H__

#include <vector>

namespace simpledet {
namespace core {

  class PixelGrid {
  public:

    PixelGrid( std::vector<float> origin, std::vector<float> grid_dimensions,
	       std::vector<int> num_pixels, std::vector<int> padding );
    virtual ~PixelGrid() {};

    std::vector<float> _origin;
    std::vector<float> _dimlen;
    std::vector<int>   _npixels;
    std::vector<int>   _nblocks;
    std::vector<float> _pixelsize;
    std::vector<int>   _padding;
    std::vector<float> _padded_length;
    std::vector<int>   _padded_npixels;
    std::vector<float> _padded_origin;

    // we store the pixel grid centers into Vec8f in order to do vectorized computations

  };
  
}
}


#endif
