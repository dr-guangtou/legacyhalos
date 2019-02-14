"""
legacyhalos.html
================

Code to generate HTML content.

"""
import os, subprocess, pdb
import numpy as np
import astropy.table

import legacyhalos.io
import legacyhalos.misc
import legacyhalos.hsc

from legacyhalos.misc import plot_style
sns = plot_style()

#import seaborn as sns
#sns.set(style='ticks', font_scale=1.4, palette='Set2')

def qa_ccd(onegal, galaxy, galaxydir, htmlgalaxydir, pixscale=0.262,
           survey=None, mp=None, clobber=False, verbose=True):
    """Build CCD-level QA.

    """
    from astrometry.util.fits import fits_table
    from legacyhalos.qa import display_ccdpos, _display_ccdmask_and_sky
    from astrometry.util.multiproc import multiproc

    if survey is None:
        from legacypipe.survey import LegacySurveyData
        survey = LegacySurveyData()

    radius_pixel = legacyhalos.misc.cutout_radius_150kpc(
        redshift=onegal['Z'], pixscale=pixscale) # [pixels]

    qarootfile = os.path.join(htmlgalaxydir, '{}-2d'.format(galaxy))
    #maskfile = os.path.join(galaxydir, '{}-custom-ccdmasks.fits.fz'.format(galaxy))

    ccdsfile = os.path.join(galaxydir, '{}-ccds.fits'.format(galaxy))
    if os.path.isfile(ccdsfile):
        ccds = survey.cleanup_ccds_table(fits_table(ccdsfile))
        print('Read {} CCDs from {}'.format(len(ccds), ccdsfile))

    okfiles = True
    for iccd in range(len(ccds)):
        qafile = '{}-ccd{:02d}.png'.format(qarootfile, iccd)
        okfiles *= os.path.isfile(qafile)

    if not okfiles or clobber:
        if mp is None:
            mp = multiproc(nthreads=1)
            
        ccdargs = [(galaxy, galaxydir, qarootfile, radius_pixel, _ccd, iccd, survey)
                   for iccd, _ccd in enumerate(ccds)]
        mp.map(_display_ccdmask_and_sky, ccdargs)
        
    ccdposfile = os.path.join(htmlgalaxydir, '{}-ccdpos.png'.format(galaxy))
    if not os.path.isfile(ccdposfile) or clobber:
        display_ccdpos(onegal, ccds, png=ccdposfile)

def qa_montage_coadds(galaxy, galaxydir, htmlgalaxydir, clobber=False, verbose=True):
    """Montage the coadds into a nice QAplot."""

    montagefile = os.path.join(htmlgalaxydir, '{}-grz-montage.png'.format(galaxy))

    if not os.path.isfile(montagefile) or clobber:
        # Make sure all the files exist.
        check = True
        jpgfile = []
        for suffix in ('custom-image-grz', 'custom-model-nocentral-grz', 'custom-image-central-grz'):
            _jpgfile = os.path.join(galaxydir, '{}-{}.jpg'.format(galaxy, suffix))
            jpgfile.append(_jpgfile)
            if not os.path.isfile(_jpgfile):
                print('File {} not found!'.format(_jpgfile))
                check = False
                
        if check:        
            cmd = 'montage -bordercolor white -borderwidth 1 -tile 3x1 -geometry +0+0 '
            cmd = cmd+' '.join(ff for ff in jpgfile)
            cmd = cmd+' {}'.format(montagefile)

            if verbose:
                print('Writing {}'.format(montagefile))
            subprocess.call(cmd.split())

def qa_ellipse_results(galaxy, galaxydir, htmlgalaxydir, band=('g', 'r', 'z'),
                       clobber=False, verbose=True):
    """Generate QAplots from the ellipse-fitting.

    """
    from legacyhalos.io import read_multiband, read_ellipsefit, read_sky_ellipsefit
    from legacyhalos.qa import (display_multiband, display_ellipsefit,
                                display_ellipse_sbprofile)

    ellipsefit = read_ellipsefit(galaxy, galaxydir)
    skyellipsefit = read_sky_ellipsefit(galaxy, galaxydir)

    if len(ellipsefit) > 0:
        # Toss out bad fits.
        indx = None
        #indx = (isophotfit[refband].stop_code < 4) * (isophotfit[refband].intens > 0)
        #indx = (isophotfit[refband].stop_code <= 4) * (isophotfit[refband].intens > 0)

        sbprofilefile = os.path.join(htmlgalaxydir, '{}-ellipse-sbprofile.png'.format(galaxy))
        if not os.path.isfile(sbprofilefile) or clobber:
            display_ellipse_sbprofile(ellipsefit, skyellipsefit=skyellipsefit,
                                      png=sbprofilefile, verbose=verbose, minerr=0.0)

        multibandfile = os.path.join(htmlgalaxydir, '{}-ellipse-multiband.png'.format(galaxy))
        if not os.path.isfile(multibandfile) or clobber:
            data = read_multiband(galaxy, galaxydir, band=band)
            display_multiband(data, ellipsefit=ellipsefit, indx=indx,
                              png=multibandfile, verbose=verbose)

        ellipsefitfile = os.path.join(htmlgalaxydir, '{}-ellipse-ellipsefit.png'.format(galaxy))
        if not os.path.isfile(ellipsefitfile) or clobber:
            display_ellipsefit(ellipsefit, png=ellipsefitfile, xlog=False, verbose=verbose)
        
def qa_mge_results(galaxy, galaxydir, htmlgalaxydir, refband='r', band=('g', 'r', 'z'),
                   pixscale=0.262, clobber=False, verbose=True):
    """Generate QAplots from the MGE fitting.

    """
    from legacyhalos.io import read_mgefit, read_multiband
    from legacyhalos.qa import display_mge_sbprofile, display_multiband
    
    mgefit = read_mgefit(galaxy, galaxydir)

    if len(mgefit) > 0:

        ## Toss out bad fits.
        #indx = (mgefit[refband].stop_code <= 4) * (mgefit[refband].intens > 0)
        #
        multibandfile = os.path.join(htmlgalaxydir, '{}-mge-multiband.png'.format(galaxy))
        if not os.path.isfile(multibandfile) or clobber:
            data = read_multiband(galaxy, galaxydir, band=band)
            display_multiband(data, mgefit=mgefit, band=band, refband=refband,
                              png=multibandfile, contours=True, verbose=verbose)
        
        #isophotfile = os.path.join(htmlgalaxydir, '{}-mge-mgefit.png'.format(galaxy))
        #if not os.path.isfile(isophotfile) or clobber:
        #    # Just display the reference band.
        #    display_mgefit(mgefit, band=refband, indx=indx, pixscale=pixscale,
        #                   png=isophotfile, verbose=verbose)

        sbprofilefile = os.path.join(htmlgalaxydir, '{}-mge-sbprofile.png'.format(galaxy))
        if not os.path.isfile(sbprofilefile) or clobber:
            display_mge_sbprofile(mgefit, band=band, refband=refband, pixscale=pixscale,
                                  png=sbprofilefile, verbose=verbose)
        
def qa_sersic_results(galaxy, galaxydir, htmlgalaxydir, band=('g', 'r', 'z'),
                      clobber=False, verbose=True):
    """Generate QAplots from the Sersic modeling.

    """
    from legacyhalos.io import read_sersic
    from legacyhalos.qa import display_sersic

    # Double Sersic
    double = read_sersic(galaxy, galaxydir, modeltype='double')
    if bool(double):
        doublefile = os.path.join(htmlgalaxydir, '{}-sersic-double.png'.format(galaxy))
        if not os.path.isfile(doublefile) or clobber:
            display_sersic(double, png=doublefile, verbose=verbose)

    # Double Sersic, no wavelength dependence
    double = read_sersic(galaxy, galaxydir, modeltype='double-nowavepower')
    if bool(double):
        doublefile = os.path.join(htmlgalaxydir, '{}-sersic-double-nowavepower.png'.format(galaxy))
        if not os.path.isfile(doublefile) or clobber:
            display_sersic(double, png=doublefile, verbose=verbose)

    # Single Sersic, no wavelength dependence
    single = read_sersic(galaxy, galaxydir, modeltype='single-nowavepower')
    if bool(single):
        singlefile = os.path.join(htmlgalaxydir, '{}-sersic-single-nowavepower.png'.format(galaxy))
        if not os.path.isfile(singlefile) or clobber:
            display_sersic(single, png=singlefile, verbose=verbose)

    # Single Sersic
    single = read_sersic(galaxy, galaxydir, modeltype='single')
    if bool(single):
        singlefile = os.path.join(htmlgalaxydir, '{}-sersic-single.png'.format(galaxy))
        if not os.path.isfile(singlefile) or clobber:
            display_sersic(single, png=singlefile, verbose=verbose)

    # Sersic-exponential
    serexp = read_sersic(galaxy, galaxydir, modeltype='exponential')
    if bool(serexp):
        serexpfile = os.path.join(htmlgalaxydir, '{}-sersic-exponential.png'.format(galaxy))
        if not os.path.isfile(serexpfile) or clobber:
            display_sersic(serexp, png=serexpfile, verbose=verbose)

    # Sersic-exponential, no wavelength dependence
    serexp = read_sersic(galaxy, galaxydir, modeltype='exponential-nowavepower')
    if bool(serexp):
        serexpfile = os.path.join(htmlgalaxydir, '{}-sersic-exponential-nowavepower.png'.format(galaxy))
        if not os.path.isfile(serexpfile) or clobber:
            display_sersic(serexp, png=serexpfile, verbose=verbose)

def make_plots(sample, datadir=None, htmldir=None, galaxylist=None, refband='r',
               band=('g', 'r', 'z'), pixscale=0.262, survey=None, nproc=1,
               maketrends=False, ccdqa=False, clobber=False, verbose=True,
               hsc=False):
    """Make QA plots.

    """
    if datadir is None:
        datadir = legacyhalos.io.legacyhalos_data_dir()
    if htmldir is None:
        htmldir = legacyhalos.io.legacyhalos_html_dir()

    if survey is None:
        from legacypipe.survey import LegacySurveyData
        survey = LegacySurveyData()

    if maketrends:
        from legacyhalos.qa import sample_trends
        sample_trends(sample, htmldir, datadir=datadir, verbose=verbose)

    if ccdqa:
        from astrometry.util.multiproc import multiproc
        mp = multiproc(nthreads=nproc)

    for ii, onegal in enumerate(sample):

        if galaxylist is None:
            if hsc:
                galaxy, galaxydir, htmlgalaxydir = legacyhalos.hsc.get_galaxy_galaxydir(onegal, html=True)
            else:
                galaxy, galaxydir, htmlgalaxydir = legacyhalos.io.get_galaxy_galaxydir(onegal, html=True)
        else:
            galaxy = galaxylist[ii]
            galaxydir = os.path.join(datadir, galaxy)
            htmlgalaxydir = os.path.join(htmldir, galaxy)
            
        if not os.path.isdir(htmlgalaxydir):
            os.makedirs(htmlgalaxydir, exist_ok=True)

        # Build the montage coadds.
        qa_montage_coadds(galaxy, galaxydir, htmlgalaxydir,
                          clobber=clobber, verbose=verbose)

        # Build the ellipse plots.
        qa_ellipse_results(galaxy, galaxydir, htmlgalaxydir, band=band,
                           clobber=clobber, verbose=verbose)
        
        qa_sersic_results(galaxy, galaxydir, htmlgalaxydir, band=band,
                          clobber=clobber, verbose=verbose)

        # Build the CCD-level QA.  This QA script needs to be last, because we
        # check the completeness of the HTML portion of legacyhalos-mpi based on
        # the ccdpos file.
        if ccdqa:
            qa_ccd(onegal, galaxy, galaxydir, htmlgalaxydir, pixscale=pixscale,
                   mp=mp, survey=survey, clobber=clobber, verbose=verbose)

        # Build the MGE plots.
        #qa_mge_results(galaxy, galaxydir, htmlgalaxydir, refband='r', band=band,
        #               clobber=clobber, verbose=verbose)

    return 1

def _javastring():
    """Return a string that embeds a date in a webpage."""
    import textwrap

    js = textwrap.dedent("""
    <SCRIPT LANGUAGE="JavaScript">
    var months = new Array(13);
    months[1] = "January";
    months[2] = "February";
    months[3] = "March";
    months[4] = "April";
    months[5] = "May";
    months[6] = "June";
    months[7] = "July";
    months[8] = "August";
    months[9] = "September";
    months[10] = "October";
    months[11] = "November";
    months[12] = "December";
    var dateObj = new Date(document.lastModified)
    var lmonth = months[dateObj.getMonth() + 1]
    var date = dateObj.getDate()
    var fyear = dateObj.getYear()
    if (fyear < 2000)
    fyear = fyear + 1900
    document.write(" " + fyear + " " + lmonth + " " + date)
    </SCRIPT>
    """)

    return js
        
def make_html(sample=None, datadir=None, htmldir=None, band=('g', 'r', 'z'),
              refband='r', pixscale=0.262, first=None, last=None, nproc=1,
              survey=None, makeplots=True, clobber=False, verbose=True,
              maketrends=False, ccdqa=True):
    """Make the HTML pages.

    """
    import subprocess
    import fitsio

    import legacyhalos.io
    from legacyhalos.misc import cutout_radius_150kpc

    if datadir is None:
        datadir = legacyhalos.io.legacyhalos_data_dir()
    if htmldir is None:
        htmldir = legacyhalos.io.legacyhalos_html_dir()

    if sample is None:
        sample = legacyhalos.io.read_sample(first=first, last=last)

    if type(sample) is astropy.table.row.Row:
        sample = astropy.table.Table(sample)

    galaxy, galaxydir, htmlgalaxydir = legacyhalos.io.get_galaxy_galaxydir(sample, html=True)

    # Write the last-updated date to a webpage.
    js = _javastring()       

    # Get the viewer link
    def _viewer_link(gal):
        baseurl = 'http://legacysurvey.org/viewer/'
        width = 2 * cutout_radius_150kpc(redshift=gal['Z'], pixscale=0.262) # [pixels]
        if width > 400:
            zoom = 14
        else:
            zoom = 15
        viewer = '{}?ra={:.6f}&dec={:.6f}&zoom={:g}&layer=ls-dr67'.format(
            baseurl, gal['RA'], gal['DEC'], zoom)
        
        return viewer

    def _skyserver_link(gal):
        if 'SDSS_OBJID' in gal.colnames:
            return 'http://skyserver.sdss.org/dr14/en/tools/explore/summary.aspx?id={:d}'.format(gal['SDSS_OBJID'])
        else:
            return ''

    trendshtml = 'trends.html'
    homehtml = 'index.html'

    # Build the home (index.html) page--
    if not os.path.exists(htmldir):
        os.makedirs(htmldir)
    homehtmlfile = os.path.join(htmldir, homehtml)

    with open(homehtmlfile, 'w') as html:
        html.write('<html><body>\n')
        html.write('<style type="text/css">\n')
        html.write('table, td, th {padding: 5px; text-align: left; border: 1px solid black;}\n')
        html.write('</style>\n')

        html.write('<h1>LegacyHalos: Central Galaxies</h1>\n')
        if maketrends:
            html.write('<p>\n')
            html.write('<a href="{}">Sample Trends</a><br />\n'.format(trendshtml))
            html.write('<a href="https://github.com/moustakas/legacyhalos">Code and documentation</a>\n')
            html.write('</p>\n')

        html.write('<table>\n')
        html.write('<tr>\n')
        html.write('<th>Number</th>\n')
        html.write('<th>Galaxy</th>\n')
        html.write('<th>RA</th>\n')
        html.write('<th>Dec</th>\n')
        html.write('<th>Redshift</th>\n')
        html.write('<th>Richness</th>\n')
        html.write('<th>Pcen</th>\n')
        html.write('<th>Viewer</th>\n')
        html.write('<th>SkyServer</th>\n')
        html.write('</tr>\n')
        for ii, (gal, galaxy1, htmlgalaxydir1) in enumerate(zip(
            sample, np.atleast_1d(galaxy), np.atleast_1d(htmlgalaxydir) )):

            htmlfile1 = os.path.join(htmlgalaxydir1.replace(htmldir, '')[1:], '{}.html'.format(galaxy1))

            html.write('<tr>\n')
            html.write('<td>{:g}</td>\n'.format(ii))
            html.write('<td><a href="{}">{}</a></td>\n'.format(htmlfile1, galaxy1))
            html.write('<td>{:.7f}</td>\n'.format(gal['RA']))
            html.write('<td>{:.7f}</td>\n'.format(gal['DEC']))
            html.write('<td>{:.5f}</td>\n'.format(gal['Z']))
            html.write('<td>{:.4f}</td>\n'.format(gal['LAMBDA_CHISQ']))
            html.write('<td>{:.3f}</td>\n'.format(gal['P_CEN'][0]))
            html.write('<td><a href="{}" target="_blank">Link</a></td>\n'.format(_viewer_link(gal)))
            html.write('<td><a href="{}" target="_blank">Link</a></td>\n'.format(_skyserver_link(gal)))
            html.write('</tr>\n')
        html.write('</table>\n')
        
        html.write('<br /><br />\n')
        html.write('<b><i>Last updated {}</b></i>\n'.format(js))
        html.write('</html></body>\n')
        html.close()

    # Build the trends (trends.html) page--
    if maketrends:
        trendshtmlfile = os.path.join(htmldir, trendshtml)
        with open(trendshtmlfile, 'w') as html:
            html.write('<html><body>\n')
            html.write('<style type="text/css">\n')
            html.write('table, td, th {padding: 5px; text-align: left; border: 1px solid black;}\n')
            html.write('</style>\n')

            html.write('<h1>LegacyHalos: Sample Trends</h1>\n')
            html.write('<p><a href="https://github.com/moustakas/legacyhalos">Code and documentation</a></p>\n')
            html.write('<a href="trends/ellipticity_vs_sma.png"><img src="trends/ellipticity_vs_sma.png" alt="Missing file ellipticity_vs_sma.png" height="auto" width="50%"></a>')
            html.write('<a href="trends/gr_vs_sma.png"><img src="trends/gr_vs_sma.png" alt="Missing file gr_vs_sma.png" height="auto" width="50%"></a>')
            html.write('<a href="trends/rz_vs_sma.png"><img src="trends/rz_vs_sma.png" alt="Missing file rz_vs_sma.png" height="auto" width="50%"></a>')

            html.write('<br /><br />\n')
            html.write('<b><i>Last updated {}</b></i>\n'.format(js))
            html.write('</html></body>\n')
            html.close()

    nextgalaxy = np.roll(np.atleast_1d(galaxy), -1)
    prevgalaxy = np.roll(np.atleast_1d(galaxy), 1)
    nexthtmlgalaxydir = np.roll(np.atleast_1d(htmlgalaxydir), -1)
    prevhtmlgalaxydir = np.roll(np.atleast_1d(htmlgalaxydir), 1)

    # Make a separate HTML page for each object.
    for ii, (gal, galaxy1, galaxydir1, htmlgalaxydir1) in enumerate( zip(
        sample, np.atleast_1d(galaxy), np.atleast_1d(galaxydir), np.atleast_1d(htmlgalaxydir) ) ):
        
        if not os.path.exists(htmlgalaxydir1):
            os.makedirs(htmlgalaxydir1)

        ccdsfile = os.path.join(galaxydir1, '{}-ccds.fits'.format(galaxy1))
        if os.path.isfile(ccdsfile):
            nccds = fitsio.FITS(ccdsfile)[1].get_nrows()
        else:
            nccds = None

        nexthtmlgalaxydir1 = os.path.join('{}'.format(nexthtmlgalaxydir[ii].replace(htmldir, '')[1:]), '{}.html'.format(nextgalaxy[ii]))
        prevhtmlgalaxydir1 = os.path.join('{}'.format(prevhtmlgalaxydir[ii].replace(htmldir, '')[1:]), '{}.html'.format(prevgalaxy[ii]))

        htmlfile = os.path.join(htmlgalaxydir1, '{}.html'.format(galaxy1))
        with open(htmlfile, 'w') as html:
            html.write('<html><body>\n')
            html.write('<style type="text/css">\n')
            html.write('table, td, th {padding: 5px; text-align: left; border: 1px solid black;}\n')
            html.write('</style>\n')

            html.write('<h1>Central Galaxy {}</h1>\n'.format(galaxy1))

            html.write('<a href="../../../../{}">Home</a>\n'.format(homehtml))
            html.write('<br />\n')
            html.write('<a href="../../../../{}">Next Central Galaxy ({})</a>\n'.format(nexthtmlgalaxydir1, nextgalaxy[ii]))
            html.write('<br />\n')
            html.write('<a href="../../../../{}">Previous Central Galaxy ({})</a>\n'.format(prevhtmlgalaxydir1, prevgalaxy[ii]))
            html.write('<br />\n')
            html.write('<br />\n')

            # Table of properties
            html.write('<table>\n')
            html.write('<tr>\n')
            html.write('<th>Number</th>\n')
            html.write('<th>Galaxy</th>\n')
            html.write('<th>RA</th>\n')
            html.write('<th>Dec</th>\n')
            html.write('<th>Redshift</th>\n')
            html.write('<th>Richness</th>\n')
            html.write('<th>Pcen</th>\n')
            html.write('<th>Viewer</th>\n')
            html.write('<th>SkyServer</th>\n')
            html.write('</tr>\n')

            html.write('<tr>\n')
            html.write('<td>{:g}</td>\n'.format(ii))
            html.write('<td>{}</td>\n'.format(galaxy1))
            html.write('<td>{:.7f}</td>\n'.format(gal['RA']))
            html.write('<td>{:.7f}</td>\n'.format(gal['DEC']))
            html.write('<td>{:.5f}</td>\n'.format(gal['Z']))
            html.write('<td>{:.4f}</td>\n'.format(gal['LAMBDA_CHISQ']))
            html.write('<td>{:.3f}</td>\n'.format(gal['P_CEN'][0]))
            html.write('<td><a href="{}" target="_blank">Link</a></td>\n'.format(_viewer_link(gal)))
            html.write('<td><a href="{}" target="_blank">Link</a></td>\n'.format(_skyserver_link(gal)))
            html.write('</tr>\n')
            html.write('</table>\n')

            html.write('<h2>Image mosaics</h2>\n')
            html.write('<p>Each mosaic (left to right: data, model of all but the central galaxy, residual image containing just the central galaxy) is 300 kpc by 300 kpc.</p>\n')
            html.write('<table width="90%">\n')
            html.write('<tr><td><a href="{}-grz-montage.png"><img src="{}-grz-montage.png" alt="Missing file {}-grz-montage.png" height="auto" width="100%"></a></td></tr>\n'.format(galaxy1, galaxy1, galaxy1))
            #html.write('<tr><td>Data, Model, Residuals</td></tr>\n')
            html.write('</table>\n')
            #html.write('<br />\n')
            
            html.write('<h2>Elliptical Isophote Analysis</h2>\n')
            html.write('<table width="90%">\n')
            html.write('<tr>\n')
            html.write('<td><a href="{}-ellipse-multiband.png"><img src="{}-ellipse-multiband.png" alt="Missing file {}-ellipse-multiband.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('</tr>\n')
            html.write('</table>\n')

            html.write('<table width="90%">\n')
            html.write('<tr>\n')
            #html.write('<td><a href="{}-ellipse-ellipsefit.png"><img src="{}-ellipse-ellipsefit.png" alt="Missing file {}-ellipse-ellipsefit.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('<td width="50%"><a href="{}-ellipse-sbprofile.png"><img src="{}-ellipse-sbprofile.png" alt="Missing file {}-ellipse-sbprofile.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('<td></td>\n')
            html.write('</tr>\n')
            html.write('</table>\n')
            
            html.write('<h2>Surface Brightness Profile Modeling</h2>\n')
            html.write('<table width="90%">\n')

            # single-sersic
            html.write('<tr>\n')
            html.write('<th>Single Sersic (No Wavelength Dependence)</th><th>Single Sersic</th>\n')
            html.write('</tr>\n')
            html.write('<tr>\n')
            html.write('<td><a href="{}-sersic-single-nowavepower.png"><img src="{}-sersic-single-nowavepower.png" alt="Missing file {}-sersic-single-nowavepower.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('<td><a href="{}-sersic-single.png"><img src="{}-sersic-single.png" alt="Missing file {}-sersic-single.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('</tr>\n')

            # Sersic+exponential
            html.write('<tr>\n')
            html.write('<th>Sersic+Exponential (No Wavelength Dependence)</th><th>Sersic+Exponential</th>\n')
            html.write('</tr>\n')
            html.write('<tr>\n')
            html.write('<td><a href="{}-sersic-exponential-nowavepower.png"><img src="{}-sersic-exponential-nowavepower.png" alt="Missing file {}-sersic-exponential-nowavepower.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('<td><a href="{}-sersic-exponential.png"><img src="{}-sersic-exponential.png" alt="Missing file {}-sersic-exponential.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('</tr>\n')

            # double-sersic
            html.write('<tr>\n')
            html.write('<th>Double Sersic (No Wavelength Dependence)</th><th>Double Sersic</th>\n')
            html.write('</tr>\n')
            html.write('<tr>\n')
            html.write('<td><a href="{}-sersic-double-nowavepower.png"><img src="{}-sersic-double-nowavepower.png" alt="Missing file {}-sersic-double-nowavepower.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('<td><a href="{}-sersic-double.png"><img src="{}-sersic-double.png" alt="Missing file {}-sersic-double.png" height="auto" width="100%"></a></td>\n'.format(galaxy1, galaxy1, galaxy1))
            html.write('</tr>\n')

            html.write('</table>\n')

            html.write('<br />\n')

            if nccds:
                html.write('<h2>CCD Diagnostics</h2>\n')
                html.write('<table width="90%">\n')
                html.write('<tr>\n')
                pngfile = '{}-ccdpos.png'.format(galaxy1)
                html.write('<td><a href="{0}"><img src="{0}" alt="Missing file {0}" height="auto" width="100%"></a></td>\n'.format(
                    pngfile))
                html.write('</tr>\n')

                for iccd in range(nccds):
                    html.write('<tr>\n')
                    pngfile = '{}-2d-ccd{:02d}.png'.format(galaxy1, iccd)
                    html.write('<td><a href="{0}"><img src="{0}" alt="Missing file {0}" height="auto" width="100%"></a></td>\n'.format(
                        pngfile))
                    html.write('</tr>\n')
                html.write('</table>\n')
                html.write('<br />\n')

            html.write('<a href="../../../../{}">Home</a>\n'.format(homehtml))
            html.write('<br />\n')
            html.write('<a href="{}">Next Central Galaxy ({})</a>\n'.format(nexthtmlgalaxydir1, nextgalaxy[ii]))
            html.write('<br />\n')
            html.write('<a href="{}">Previous Central Galaxy ({})</a>\n'.format(prevhtmlgalaxydir1, prevgalaxy[ii]))
            html.write('<br />\n')

            html.write('<br /><b><i>Last updated {}</b></i>\n'.format(js))
            html.write('<br />\n')
            html.write('</html></body>\n')
            html.close()

    # Make the plots.
    if makeplots:
        err = make_plots(sample, datadir=datadir, htmldir=htmldir, refband=refband,
                         band=band, pixscale=pixscale, survey=survey, clobber=clobber,
                         verbose=verbose, nproc=nproc, ccdqa=ccdqa, maketrends=maketrends)

    cmd = '/usr/bin/chgrp -R cosmo {}'.format(htmldir)
    print(cmd)
    err1 = subprocess.call(cmd.split())

    cmd = 'find {} -type d -exec chmod 775 {{}} +'.format(htmldir)
    print(cmd)
    err2 = subprocess.call(cmd.split())

    cmd = 'find {} -type f -exec chmod 664 {{}} +'.format(htmldir)
    print(cmd)
    err3 = subprocess.call(cmd.split())

    if err1 != 0 or err2 != 0 or err3 != 0:
        print('Something went wrong updating permissions; please check the logfile.')
        return 0
    
    return 1