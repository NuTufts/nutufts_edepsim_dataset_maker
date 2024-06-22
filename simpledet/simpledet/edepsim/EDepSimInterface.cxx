#include "EDepSimInterface.h"
#include "TH2D.h"

#include <cmath>

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
  if ( nhits==0 ) {
    // return empty histogram
    TH2D himage("himage", "", 1, origin[0], max_gridpt[0], 1, origin[1], max_gridpt[1] );
    return himage;
  }

  // get time of first edep. based on how geant4 tracks particles, this should be the first
  // position of energy deposition
  auto const first_hit = hit_container.at(0);
  // we want to fix the start of the shower at:
  // (z=100 cm, y=0 cm)
  std::vector<float> first_edep(4,0);
  for (int i=0; i<3; i++)
    first_edep[i]  = (first_hit.GetStart()[i])*0.1; /// mm -> cm
  first_edep[3] = first_hit.GetStart()[3]; // geant4 time in ns
  
  std::vector<float> offset(2,0); // (100 cm, 50 cm) = (z,y) - offset
  float t0 = first_edep[3];
  offset[0] = first_edep[2]-100.0;
  offset[1] = first_edep[1]-0.0;


  const float max_step_size = 0.03;
  
  for (size_t ihit=0; ihit<nhits; ihit++) {

    auto const& hit = hit_container.at(ihit);

    // each hit is a line segment
    std::vector<float> start(4);
    std::vector<float> stop(4);
    std::vector<float> stepdir(4);
    for (int i=0; i<3; i++) {
      start[i] = hit.GetStart()[i]*0.1; // mm->cm
      stop[i]  = hit.GetStop()[i]*0.1;  // mm->cm
      stepdir[i] = stop[i]-start[i];
    }
    start[3] = hit.GetStart()[3]; // ns
    stop[3] = hit.GetStop()[3]; // ns
    stepdir[3] = stop[3]-start[3]; // ns
    
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

      // // --------------------------------------------
      // // spread energy based on location of line segment

      // // find pixel location
      // // z-dimension
      // int iz0 = ( (pt0[2]-offset[0])-origin[0])/pixelsize[0]; 
      // int iz1 = ( (pt1[2]-offset[0])-origin[0])/pixelsize[0];
      // int idz = iz1-iz0; // should be either -1, 0, 1
      // int dzdz = idz*idz; // either 1 or 0
      // int izplane  = iz0 + (idz+1)/2;
      // float zplane = origin[0] + float(izplane)*pixelsize[0];

      // // same pixel
      // float zlen2_d0 = (pt1[2]-pt0[2])*(pt1[2]-pt0[2]);
      // // different pixel, so distanace to plane
      // float zlen2_d1 = ( zplane-(pt0[2]-offset[0]) )*( zplane - (pt0[2]-offset[0]) );
      // float zlen2 = zlen2_d0*(dzdz+1) + zlen2_d1*(dzdz);
      
      // // y-dimension
      // int iy0 = ( (pt0[1]-offset[1]) - origin[1])/pixelsize[1];
      // int iy1 = ( (pt1[1]-offset[1]) - origin[1])/pixelsize[1];
      // int idy = iy1-iy0;
      // int dydy = idy;
      // int iyplane  = iy0 + (idy+1)/2;
      // float yplane = origin[1] + float(iyplane)*pixelsize[1];

      // // same pixel
      // float ylen2_d0 = (pt1[1]-pt0[1])*(pt1[1]-pt0[1]);
      // // different pixel, so distanace to plane
      // float ylen2_d1 = (yplane - (pt0[1]-offset[1]) )*(yplane - (pt0[1]-offset[1]) );
      // float ylen2 = ylen2_d0*(dydy+1) + ylen2_d1*(dydy);

      // // div length
      // float ll = sqrt( zlen2 + ylen2 );
      // // Efrac
      // float Efrac = Estep*ll/divlen;
      // int ipix = iy0*npixels[0] + iz0;
      // if (ipix<0 || ipix>=(int)image.size()) {
      // 	std::cout << "ipix=" << ipix << std::endl;
      // 	continue;
      // }
      // image[ipix] += Efrac;      
      // ----------------------------------------------------

      // distribute via approximate gaussian kernel using tranverse diffusion
      // A. Lister, approximate spread:
      // 1.4 mm longitudinal over full 256.0 cm drift
      // 2.5 mm transverse drift over full 256.0 cm drift
      // each pixel is 3.0 mm, so we can limit our gaussian kernel to -3,+3 bins, a 7x7 Gaussian kernel
      // we make the kernel, taking into account the relative offset
      // based on x-position in middle of detector 125.0

      // get pos relative to origin, i.e. our plane coordinates
      std::vector<float> pos(2,0);
      // pos[0] = midpt[2]-offset[0];
      // pos[1] = midpt[1]-offset[1];
      pos[0] = midpt[2];
      pos[1] = midpt[1];
      
      std::vector<float> planepos(2,0);
      planepos[0] = pos[0]-origin[0]; // z-position
      planepos[1] = pos[1]-origin[1]; // y-position
      int izpix = planepos[0]/pixelsize[0];
      int iypix = planepos[1]/pixelsize[1];
      std::vector<float> pixcenter(2,0);
      pixcenter[0] = (float(izpix)+0.5)*pixelsize[0];
      pixcenter[1] = (float(iypix)+0.5)*pixelsize[1];

      float dz_offset = planepos[0]-pixcenter[0];
      float dy_offset = planepos[1]-pixcenter[1];
      
      float sigma = (midpt[0]+125.0)*(0.25/256.0);
      // std::cout << "------------------------" << std::endl;
      // std::cout << "midpt: " << midpt[2] << " " << midpt[1] << std::endl;
      // std::cout << "pos: " << pos[0] << " " << pos[1] << std::endl;
      // std::cout << "planepos: " << planepos[0] << " " << planepos[1] << std::endl;
      // std::cout << "pixelindex: " << izpix << " " << iypix << std::endl;
      // std::cout << "pixcenter: " << pixcenter[0] << " " << pixcenter[1] << std::endl;
      // std::cout << "pos relative to pixcenter: " << dz_offset << " " << dy_offset << std::endl;
      // std::cout << "sigma: " << sigma << " x=" << midpt[0] << std::endl;

      // simple binning fill
      // int ipix = (iypix)*npixels[0] + (izpix);
      // if ( ipix>=0 && ipix<image.size() ) {
      // 	image[ipix] = Estep/float(ndivs);
      // }

      // apply approximate kernel
      float sum = 0.0;
      float kernel[7][7] = {0.0};
      for (int ikz=-3; ikz<=3; ikz++) {
	for (int iky=-3; iky<=3; iky++) {
	  // position of kernel pixel relative to center
	  float kpixz = float(ikz)*pixelsize[0];
	  float kpixy = float(iky)*pixelsize[1];
	  float dist2 = (kpixz-dz_offset)*(kpixz-dz_offset) + (kpixy-dy_offset)*(kpixy-dy_offset);
	  float arg = -0.5*dist2/(sigma*sigma);
	  float w = exp(arg);
	  kernel[3+ikz][3+iky] = w;
	  sum += w;
	}
      }
      

      // Efrac
      float Efrac = Estep/float(ndivs);
      for (int ikz=-3; ikz<=3; ikz++) {
	for (int iky=-3; iky<=3; iky++) {
	  int ipix = (iypix+iky)*npixels[0] + (izpix+ikz);
	  if ( ipix>=0 && ipix<(int)image.size() )
	    image[ipix] += Efrac*kernel[3+ikz][3+iky]/sum;
	}
      }
      
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
