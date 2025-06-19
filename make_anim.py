import glob
from utils import _get_round_number, _color_ax_to_white, Result, HERE, LATEX, RANGES, OUTDIR, images_to_transparent_gif, concat_pngs_side_by_side
from tqdm.auto import tqdm
from custom_corner import plot_custom_corner
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

ONE_D_YLIM_RANGES = [
    [0, 706.242],
    [0, 4.645],
    [0, 38.863],
    [0, 14.325]
]

JSDIV = pd.read_csv(f'{HERE}/data/variable_kldists_hist.csv')[['npts', 'js']]

files = []

#
files = glob.glob(f'{HERE}/data/*.json')
files = sorted(files, key=lambda x: _get_round_number(x))
reference_result = Result.load(files[-1])

for f in tqdm(files, desc='Loading results'):
    result = Result.load(f)

    fig = plot_custom_corner(
        chains=[result.posterior, reference_result.posterior],
        ylim_ranges=ONE_D_YLIM_RANGES,
        chainLabels=[
            f"LnL Surrogate ($N={result.npts}$)",
            f"Reference ($N=1,000$)",
        ],
        truths=[reference_result.truth],
        paramNames=[LATEX[l] for l in reference_result.labels],
        colorsOrder=['purples', 'lightgray'],
        # plotName=f'{OUTDIR}/npts_{result.npts}.pdf',
        paramRanges=[RANGES[l] for l in reference_result.labels],
        figureSize='AandA_page',
        customLegendFont=dict(size=15)
    )
    fname_corner = f'{OUTDIR}/npts_{result.npts}_corner.png'
    fig.savefig(fname_corner, bbox_inches='tight',  dpi=450, transparent=True)
    plt.close(fig)

    # plot 2 -- the JSD
    fname_jsd = f'{OUTDIR}/npts_{result.npts}_jsdiv.png'
    fig = plt.figure(figsize=(2.7, 2))
    plt.plot(JSDIV['npts'], JSDIV['js'], linestyle='-', color='lightgray')
    plt.scatter(result.npts, JSDIV.loc[JSDIV['npts'] == result.npts, 'js'], color='#c79af0', zorder=10)
    plt.xlabel('Number of points')
    plt.ylabel('JSD')

    # all axes spines, ticks labels to white
    ax = plt.gca()
    _color_ax_to_white(ax)
    fig.patch.set_facecolor('none')

    plt.savefig(fname_jsd, bbox_inches='tight', dpi=450, transparent=True)
    plt.close()

    concat_pngs_side_by_side(
        fname_corner, fname_jsd, f'{OUTDIR}/npts_{result.npts}.png'
    )

files = [f'{OUTDIR}/npts_{npts}.png' for npts in JSDIV['npts']]
images_to_transparent_gif(
    files,
    output_path=f'{OUTDIR}/corner_animation.gif',
    duration=1000,  # duration in milliseconds
    loop=0  # 0 means infinite loop
)




