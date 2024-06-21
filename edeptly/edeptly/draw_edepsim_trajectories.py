import numpy as np
import plotly
import plotly.graph_objects as go

PDG_COLORS = {11:"rgb(0,0,255)",
              13:"rgb(255,0,0)",
              211:"rgb(255,102,0)",
              2212:"rgb(102,0,102)",
              2112:"rgb(100,100,100)"}
              

def draw_edepsim_trajectory( traj ):
    """
    arguments
    
    traj: assumed to be a TG4Trajectory object. See cenns/io/TG4Trajectory.hh.

    return: plotly go Scatter3D plot configured to be a line plot.
    """

    npts = traj.Points.size()
    pos = np.zeros( (npts,3) )
    for ii in range(npts):
        pt = traj.Points.at(ii)
        for v in [0,1,2]:
            pos[ii,v] = pt.GetPosition()[v]
    xpdg = np.abs( traj.PDGCode )
    xcolor = "rgb(20,20,20)"
    if xpdg in PDG_COLORS:
        xcolor = PDG_COLORS[xpdg]
    plot = go.Scatter3d( x=pos[:,0], y=pos[:,1], z=pos[:,2], mode='lines', line={"color":xcolor}, name="[%d] pid=%d"%(traj.GetTrackId(),traj.GetPDGCode()) )
    return plot

    
def draw_edepsim_event_trajectories( event ):
    """
    """
    ntrajs = event.Trajectories.size() 
    plot_v = []
    for t in range(ntrajs):
        traj = event.Trajectories.at(t)
        plot = draw_edepsim_trajectory( traj )
        plot_v.append(plot)
    return plot_v

def dump_edepsim_event_trajectory_list(event):
    print("/// True Trajectories from TG4Event ////////")
    ntrajs = event.Trajectories.size()
    for t in range(ntrajs):
        traj = event.Trajectories.at(t)
        Mass = traj.GetInitialMomentum().Mag()
        E = traj.GetInitialMomentum().E()
        KE=E-Mass
        KEstr = "%.1f MeV"%(KE)
        if KE<1.0:
            KEstr = "%.1f keV"%(KE*1000.0)
        elif KE>=1000.0:
            KEstr = "%.1f GeV"%(KE*1e-3)
        elif KE<0.001:
            KEstr = "%.1f eV"%(KE*1.0e6)

        if traj.Edep_eV<1e-1:
            edepstr = " edep=%.1f meV"%(traj.Edep_eV*1e3),
        elif traj.Edep_eV<1e6:
            edepstr = " edep=%.1f eV"%(traj.Edep_eV),
        elif traj.Edep_eV<1e9:
            edepstr = " edep=%.1f MeV"%(traj.Edep_eV*1e-6),
        else:
            edepstr = " edep=%.1f GeV"%(traj.Edep_eV*1e-9),
            
        print("  [",t,"] pdg=",traj.GetPDGCode(),
              " KE=%s"%(KEstr),
            " p=(%.1f,%.1f,%.1f)"%(traj.GetInitialMomentum().X(),traj.GetInitialMomentum().Y(),traj.GetInitialMomentum().Z()),
              "%s"%(edepstr),
              " NPts=",traj.Points.size(),
              " TrackId=",traj.GetTrackId(),
              " ParentId=",traj.GetParentId())
    return
