#include "PixelGrid.h"

namespace simpledet {
namespace core {

  PixelGrid::PixelGrid( std::vector<float> origin, std::vector<float> grid_dimensions,
			std::vector<int> num_pixels, std::vector<int> padding  )
    : _origin(origin),
      _dimlen(grid_dimensions),
      _npixels(num_pixels),
      _padding(padding)
  {
    
  }

  // void PixelGrid::DefineReadoutGrid()
  // {
  //   int ntotdims = grid_dimensions.size();
  //   int npixeldims = 0;

  //   // we define the pixelsize
  //   _pixelsize.clear();
  //   _pixelsize.resize(ntotdims,0.0);
    
  //   for (int idim=0; idim<ntotdims; idim++) {

  //     // if number of pixels in this dim is zero, we do not partition in this grid
  //     if ( _npixels[idim]<=1 )
  // 	_npixels[idim] = 1.0;
  // 	continue;

  //     // increment number of dimensions with pixels
  //     npixeldims += 1;

  //     // size per pixel
  //     _pixelsize[idim] = _dimlen[idim]/float(num_pixels[idim]);

  //     // define padded grid
  //     // this lets us avoid if statements in our vectorized loop
  //     _padded_length[idime] = _pixelsize[idim]*_padded_npixels[idim];
  //     _padded_npixels[idim] = num_pixels[idim] + 2.0*padding[idim];
  //     _padded_origin[idim]  = _origin[idim] - padding[idim]*_pixelsize[idim];
      
  //   }
    
  // }
  
}
}
