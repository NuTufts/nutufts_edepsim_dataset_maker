#include "EDepSimInterface.h"
#include "TH2D.h"

namespace simpledet {
namespace edepsim {

  
TH2D EDepSimInterface::processSegmentHits( const TG4HitSegmentContainer& hit_container )
{

  // hard code stuff for now, then generalize later to focus
  const int padding[2] = { 5, 5 }; // pixels
  const float pixelsize[2] = { 0.3, 0.3 }; //cm
  const int npixels[2] = { 3456 + 2*5, 780 + 2*5 };

  // pixel grid is in the Z-Y plane

  float origin[2] = { 0.0, 0.0};
  float planelen[2] = {0.0, 0.0};
  float max_gridpt[2] = {0.0,0.0};
  for (int i=0; i<2; i++) {
    origin[i] = -pixelsize[i]*(npixels[i]/2+padding[i]);
    planelen[i] = npixels[i]*pixelsize[i];
    max_gridpt[i] = origin[i] + planelen[i];
  }

  std::vector<float> image( npixels[0]*npixels[1], 0.0 );
  std::cout << "making image with " << image.size() << " pixels" << std::endl;
  
  size_t nhits = hit_container.size();


  const float max_step_size = 0.03;
  
  for (size_t ihit=0; ihit<nhits; ihit++) {

    auto const& hit = hit_container.at(ihit);

    // each hit is a line segment
    std::vector<float> start(4);
    std::vector<float> stop(4);
    std::vector<float> stepdir(4);
    for (int i=0; i<4; i++) {
      start[i] = hit.GetStart()[i];
      stop[i]  = hit.GetStop()[i];
      stepdir[i] = stop[i]-start[i];
    }
    
    float steplen = 0.0;
    for (int i=0; i<3; i++)
      steplen += stepdir[i]*stepdir[i];
    steplen = sqrt(steplen);
    
    for (int i=0; i<3; i++)
      stepdir[i] /= steplen;

    float Estep = hit.GetEnergyDeposit();

    // we divide the line segment into
    // small pieces
    // we then assign each segment to one or two pixels
    int ndivs = steplen/max_step_size + 1;
    float divlen = steplen/float(ndivs); // change the division size to be smaller, but fit exaclty on line

    for (int istep=0; istep<ndivs; istep++) {
      
      float fstep = (float)istep;
      std::vector<float> pt0(3,0.0);
      std::vector<float> pt1(3,0.0);
      std::vector<float> midpt(3,0.0);
      for (int i=0; i<3; i++) {
	pt0[i] = start[i] + divlen*fstep*stepdir[i];
	pt1[i] = start[i] + divlen*(fstep+1.0)*stepdir[i];
	midpt[i] = 0.5*pt0[i] + 0.5*pt1[i];
      }
	
      // find pixel location
      // z-dimension
      int iz0 = (pt0[2]-origin[2])/pixelsize[0]; 
      int iz1 = (pt1[2]-origin[2])/pixelsize[0];
      int idz = iz1-iz0; // should be either -1, 0, 1
      int dzdz = idz*idz; // either 1 or 0
      int izplane  = iz0 + (idz+1)/2;
      float zplane = origin[0] + float(izplane)*pixelsize[0];

      // same pixel
      float zlen2_d0 = (pt1[2]-pt0[2])*(pt1[2]-pt0[2]);
      // different pixel, so distanace to plane
      float zlen2_d1 = (zplane-pt0[2])*(zplane-pt0[2]);
      float zlen2 = zlen2_d0*(dzdz+1) + zlen2_d1*(dzdz);
      
      // y-dimension
      int iy0 = (pt0[1]-origin[1])/pixelsize[1];
      int iy1 = (pt1[1]-origin[1])/pixelsize[1];
      int idy = iy1-iy0;
      int dydy = idy;
      int iyplane  = iy0 + (idy+1)/2;
      float yplane = origin[1] + float(iyplane)*pixelsize[1];

      // same pixel
      float ylen2_d0 = (pt1[1]-pt0[1])*(pt1[1]-pt0[1]);
      // different pixel, so distanace to plane
      float ylen2_d1 = (yplane-pt0[1])*(yplane-pt0[1]);
      float ylen2 = ylen2_d0*(dydy+1) + ylen2_d1*(dydy);

      // div length
      float ll = sqrt( zlen2 + ylen2 );

      // Efrac
      float Efrac = Estep*ll/divlen;

      int ipix = iy0*npixels[0] + iz0;
      if (ipix<0 || ipix>=image.size()) {
	std::cout << "ipix=" << ipix << std::endl;
	continue;
      }
      image[ipix] += Efrac;
      
    }//loop over ndivisions
    
  }//loop over hits

  // convert to TH2D to test
  TH2D himage("himage", "", npixels[0], origin[0], max_gridpt[0], npixels[1], origin[1], max_gridpt[1] );
  for (int iiz=0; iiz<npixels[0]; iiz++) {
    for (int iiy=0; iiy<npixels[1]; iiy++) {
      int ipix = iiy*npixels[0] + iiz;
      himage.SetBinContent( iiz+1, iiy+1, image[ipix] );
    }
  }

  return himage;
}

}
}
