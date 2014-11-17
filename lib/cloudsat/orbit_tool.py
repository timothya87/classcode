""" modified 2012/11/23 to eliminate need for matlab
    modified 2014/11/07 change I/O format and performance
    modified 2014/11/08 rename as orbit_tool
                        add a simple function: 'segment_orbit'
    modified 2014/11/11 add 'draw_CloudSat_1Dvar', draw_CloudSat_2Dvar'
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from cloudsat_tool import get_geo

def draw_orbit(radarFile, lonlim=None, latlim=None, time_step=1000, label_step=2, saveid=0):
    """
    ======================================================================
    Plot the orbit info. on a map
    ----------------------------------------------------------------------
    draw_orbit(radarFile, time_step=1000, label_step=2, saveid=0):
    ----------------------------------------------------------------------
    Input:
        radarFile: a string specify the location of CloudSat File.
        time_step: how many times (in seconds) each point represents.
        label_step: label_step=n means label every n points.
        saveid: save the output figure (=1) or not (=0).
    ======================================================================
    """
    if lonlim is None:
        lonlim=[-360, 360]
    if latlim is None
        latlim=[-90, 90]
    lat, lon, time_vals, time_seconds, dem_elevation = get_geo(radarFile)
    lat_str=lat-1; lon_str=lon+4 # lat/lon for labels
    # plot orbit using the radar ground track
    fig=plt.figure(figsize=(15, 15))
    axis=plt.gca()
    lon_mid=0
#   proj = Basemap(projection='vandg', lon_0=lon_mid)
    proj = Basemap(projection='mill', resolution='c', \
        llcrnrlat=latlim[0], urcrnrlat=latlim[1], \
        llcrnrlon=lonlim[0], urcrnrlon=lonlim[1])
    proj.drawcoastlines()
    # draw parallels and meridians.
    proj.drawparallels(np.arange(-60, 90, 30), labels=[1, 0, 0, 0])
    proj.drawmeridians(np.arange(0, 360, 60), labels=[0, 0, 0, 1])
    x, y=proj(lon, lat)
    x_str, y_str=proj(lon_str, lat_str)
    proj.plot(x, y, linewidth=3.5, color='k', linestyle='-')
    for i in np.arange(0, len(time_vals), time_step):
        # every timestep
        proj.plot(x[i], y[i], 'bo', markersize=8)
        # labelling 
        if(i % (time_step*label_step) == 0):
            time_string=time_vals[i].strftime('%H:%M UCT')
            axis.text(x_str[i], y_str[i], '{0:s}'.format(time_string), \
                  fontsize=8, fontweight='bold', ha='left', \
                  bbox={'edgecolor':'w', 'facecolor':'w', 'alpha':0.875, 'pad':0})   
    # starting point in red
    proj.plot(x[0], y[0], 'ro', markersize=8)
    [i.set_linewidth(2) for i in axis.spines.itervalues()]
    title_str='CloudSat Track\nGranule Number: ' + radarFile[-40:-35]
    axis.set_title(title_str, fontsize=14, fontweight='bold')
    if saveid==1:
        plt.savefig('_figures/03_CloudSat_track.png', dpi=450, facecolor='w', edgecolor='w',
            orientation='portrait', papertype='a4', format='png',
            transparent=True, bbox_inches='tight', pad_inches=0,
            frameon=None)
    plt.show()
    
def segment_orbit(X, Xlim):
    '''
    ======================================================================
    Segment the orbit (horizontally or vertically) based on the input
    ----------------------------------------------------------------------
    xlim_indices = segment_orbit(X, Xlim):
    ----------------------------------------------------------------------
    Input:
        X: CloudSat's longitude, latitude or seconds, 1-D numpy array.
        Xlim: 2 element list idicats where to start and where to end, 1-D list.
    Output:
        xlim_indices: Indices of start/end elements of lat/lon/seconds.
    Note:
        X and Xlim must have the same physical mean, e.g. if you want to
            segment via latitude, then X is latitude, Xlim is latlim.
        How to get segmented data:
            height_segmented=height[xlim_indices[0]:xlim_indices[1], :]
    ======================================================================  
    '''
    x_start = np.searchsorted(X.flat, Xlim[0], 'right')-1
    x_end = np.searchsorted(X.flat, Xlim[1], 'right')-1
    xlim_indices=[x_start, x_end]
    return xlim_indices
    
def draw_CloudSat_1Dvar(lon, lat, time, z, var_name, title_name, fig_name=None):
    """
    ======================================================================
    Plot the CloudSat 1D var with orbit info.
    !!! Warnning sometimes not works very well
    ----------------------------------------------------------------------
    draw_CloudSat_1Dvar(lon, lat, time, z, var_name, title_name, fig_name):
    ----------------------------------------------------------------------
    Input:
        lon, lat, time: comes from cloudsat_tool.get_geo, time is the datetime object;
        z: 1-D var to plot;
        var_name: the name of the variable shows on the figure;
        title_name: title of the figure;
        fig_name: ='$PATH/figname.png', =None if you don't want to save the figure.
    Note: Only *.png supported, sometime not wors well
    ======================================================================
    """
    from mpl_toolkits.axes_grid1 import host_subplot
    import mpl_toolkits.axisartist as AA
    # fig
    fig=plt.figure(figsize=(10, 5))
    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(bottom=0.25)
    # divide axis
    par2 = host.twiny()
    par3 = host.twiny()
    offset = -25
    new_fixed_axis = par2.get_grid_helper().new_fixed_axis
    par2.axis["top"] = new_fixed_axis(loc="bottom", axes=par2, offset=(0, offset))
    offset = -62.5
    new_fixed_axis = par3.get_grid_helper().new_fixed_axis
    par3.axis["top"] = new_fixed_axis(loc="bottom", axes=par3, offset=(0, offset))
    # label axis
    host.set_ylabel(var_name)
    host.set_xlabel('\n\nGeolocation (longitude/latitude)')
    par3.set_xlabel('Orbit time')
    # set axis lim
    par2.set_xlim(lat.min(), lat.max())
    par3.set_xlim(0, 1)
    host.set_xlim(lon.min(), lon.max())
    host.set_ylim(z.min()-0.1*(z.max()-z.min()), z.max()+0.1*(z.max()-z.min()))
    # plot
    host.plot(lon, z, linewidth=1.5, linestyle='-', color='k')
    # labelling ticks
    host.set_yticks(np.linspace(z.min(), z.max(), 5))
    host.set_xticks(np.linspace(lon.min(), lon.max(), 6))
    par2.set_xticks(np.linspace(lat.min(), lat.max(), 6))
    par2.invert_xaxis()
    count=0; labels_str=[0] * 6
    for time_id in np.linspace(0, len(time)-1, 6).astype(int):
        labels_str[count]=time[time_id].strftime('%H:%M UCT')
        count+=1
    par3.set_xticklabels(labels_str)
    # grid on
    host.grid()
    # title
    host.set_title(title_name, fontsize=14, fontweight='bold')
    # save
    if(fig_name != None):
        plt.savefig(fig_name, dpi=450, facecolor='w', edgecolor='w', \
                    orientation='portrait', papertype='a4', format='png', \
                    transparent=True, bbox_inches='tight', pad_inches=0, \
                    frameon=None)
    plt.show()
    
def draw_CloudSat_2Dvar(lon, lat, height, elev, time, z, CMap, var_name, title_name, fig_name=None):
    """
    ======================================================================
    Plot the CloudSat 2D var with orbit info.
    !!! Warnning sometimes not works very well
    ----------------------------------------------------------------------
    draw_CloudSat_2Dvar(lon, lat, height, elev, time, z, CMap, var_name, title_name, fig_name):
    ----------------------------------------------------------------------
    Input:
        lat, time: comes from cloudsat_tool.get_geo, time is the datetime object;
        lon, height, z: 2-D longitude, height and var need to plot;
        var_name: the name of the variable shows on the figure;
        title_name: title of the figure;
        fig_name: ='$PATH/figname.png', =None if you don't want to save the figure.
    Note: Only *.png supported, sometime not wors well
    ======================================================================
    """
    from mpl_toolkits.axes_grid1 import host_subplot
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import mpl_toolkits.axisartist as AA
    fig=plt.figure(figsize=(15, 5))
    host = host_subplot(111, axes_class=AA.Axes)
    # generate a "handle" for the main axis
    divider=make_axes_locatable(host)
    #
    plt.subplots_adjust(bottom=0.25)
    par2 = host.twiny()
    par3 = host.twiny()
    offset = -25
    new_fixed_axis = par2.get_grid_helper().new_fixed_axis
    par2.axis["top"] = new_fixed_axis(loc="bottom", axes=par2, offset=(0, offset))
    offset = -62.5
    new_fixed_axis = par3.get_grid_helper().new_fixed_axis
    par3.axis["top"] = new_fixed_axis(loc="bottom", axes=par3, offset=(0, offset))
    host.set_ylabel('Height ( km )')
    host.set_xlabel('\n\nGeolocation (longitude/latitude)')
    par3.set_xlabel('Orbit time')
    par2.set_xlim(lat.min(), lat.max())
    par3.set_xlim(0, 1)
    host.set_xlim(lon.min(), lon.max())
    host.set_ylim(-5.0, 12.75)
    # pcolor
    CS=host.pcolor(lon, height, z, cmap=CMap, vmin=z.min(), vmax=z.max())
    # divide a place form axis for colorbar
    CAx=divider.append_axes('right', size='5%', pad=0.75)
    #
    CBar=plt.colorbar(CS, cax=CAx)
    CBar.set_label(var_name, fontsize=12, fontweight='bold')
    CBar.ax.tick_params(axis='y', length=0)
    # fill the elev
    baseline=-5*np.ones(elev.shape).flat[:]
    host.fill_between(lon[:, 0].flat[:], elev.flat[:], baseline, \
                      where=elev.flat[:]>=baseline, facecolor=[0.5, 0.5, 0.5], interpolate=False)
#   host.set_yticks(np.linspace(z.min(), z.max(), 5))
    host.set_xticks(np.linspace(lon.min(), lon.max(), 6))
    par2.set_xticks(np.linspace(lat.min(), lat.max(), 6))
    par2.invert_xaxis()
    count=0; labels_str=[0] * 6
    for time_id in np.linspace(0, len(time)-1, 6).astype(int):
        labels_str[count]=time[time_id].strftime('%H:%M UCT')
        count+=1
    par3.set_xticklabels(labels_str)
    host.grid()
    host.set_title(title_name, fontsize=14, fontweight='bold')
    if(fig_name != None):
        plt.savefig(fig_name, dpi=450, facecolor='w', edgecolor='w', \
                    orientation='portrait', papertype='a4', format='png', \
                    transparent=True, bbox_inches='tight', pad_inches=0, \
                    frameon=None)
    plt.show()
    




                      
