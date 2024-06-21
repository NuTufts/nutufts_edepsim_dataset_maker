import numpy as np
import plotly
import plotly.graph_objects as go


def draw_edepsim_points( event, color="rgb(102,102,153)", mode="lines" ):

    detnames = event.GetSegmentDetectorNameList()
    ndets = detnames.size()
    seg_plot_v = []
    for idet in range(ndets):
        segname = detnames.at(idet)
        seghits = event.SegmentDetectors[segname]
        nseghits = seghits.size()

        #segpos = np.zeros( (2*nseghits,3) )
        #customdata = np.zeros( 2*nseghits, dtype=np.float64 )
        for ihit in range(nseghits):
            hit = seghits.at(ihit)
            hitline = np.zeros( (2,3 ))
            
            for i in range(3):
                hitline[0,i] = hit.GetStart()[i]
                hitline[1,i] = hit.GetStop()[i]
            # if hit.Contrib.size()>0:
            #     customdata[2*ihit]   = hit.Contrib[0]
            #     customdata[2*ihit+1] = hit.Contrib[0]            
            # else:
            #     customdata[2*ihit]   = -1
            #     customdata[2*ihit+1] = -1
            # customdata[2*ihit]   = idet
            # customdata[2*ihit+1] = idet  
            hitplot = go.Scatter3d(x=hitline[:,0],y=hitline[:,1], z=hitline[:,2],
                    mode="markers+lines",
                    name="%s:%d"%(segname,ihit),
                    marker={"size":2.0,"color":color},
                    line={"width":1.0,"color":color})
            seg_plot_v.append(hitplot)
    
    return seg_plot_v

def dump_edepsim_points( event ):
    nsegdets = event.SegmentDetectors.size()

    for segname in ["edepseg","vetoedep"]:
        
        seghits = event.SegmentDetectors[segname]
        nseghits = seghits.size()

        print("////// EDEPSIM[",segname,"] Hit List, NHits=%d ///////"%(nseghits))
        for ihit in range(nseghits):
            hit = seghits.at(ihit)
            contriblist = [int(hit.Contrib[i]) for i in range(hit.Contrib.size()) ]
            pdgList = [ (int)(hit.PDG_v[i]) for i in range(hit.PDG_v.size()) ]
            if hit.GetEnergyDeposit()>0.1:
                edepstr = "%.1f"%(hit.GetEnergyDeposit())
            else:
                edepstr = "%.1e"%(hit.GetEnergyDeposit())
            print(" [",ihit,"] Edep=",edepstr," MeV",
                  " start=(%.1f,%.1f,%.1f)"%(hit.Start[0],hit.Start[1],hit.Start[2]),
                  " end=(%.1f,%.1f,%.1f)"%(hit.Stop[0],hit.Stop[1],hit.Stop[2]),
                  " vol=",hit.PVname,
                  " primid=%d"%(hit.PrimaryId),
                  " contrib=",contriblist,
                  " pdgs=",pdgList)
        print("////// End of EdepSim Hit List ////////")
    
    return
