import glob
from special_corner import plotGTC
from tqdm.auto import tqdm
import numpy as np
import matplotlib.pyplot as plt
import json
import dataclasses
import pandas as pd
import glob
import os

from PIL import Image

def concat_pngs_side_by_side(img_path1, img_path2, output_path):
    """
    Concatenate two PNGs side-by-side without resizing.
    Keeps transparency (alpha channel).
    """
    img1 = Image.open(img_path1).convert("RGBA")
    img2 = Image.open(img_path2).convert("RGBA")

    # Get max height and total width
    max_height = max(img1.height, img2.height)
    total_width = img1.width + img2.width

    # Create a new transparent image
    new_img = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))

    # Paste both images
    new_img.paste(img1, (0, 0))

    # paste the second image to the right of the first -- make sure thst the bottoms
    # are aligned
    new_img.paste(img2, (img1.width, max_height - img2.height))



    new_img.save(output_path)
    # print(f"Saved to {output_path}")
    os.remove(img_path1)
    os.remove(img_path2)


HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)

JSDIV = pd.read_csv(f'{HERE}/data/variable_kldists_hist.csv')[['npts', 'js']]

LATEX = dict(
    aSF=r'$a_\mathrm{SF}$',
    dSF=r'$d_\mathrm{SF}$',
    mu_z=r'$\mu_z$',
    sigma_0=r'$\sigma_0$'
)

RANGES = dict(
    aSF=(np.inf, -np.inf),
    dSF=(np.inf, -np.inf),
    mu_z=(np.inf, -np.inf),
    sigma_0=(np.inf, -np.inf),
)

RANGES = {
    'aSF': (0.005, 0.015),
    'dSF': (4.2, 5.2),
    'mu_z': (-0.4931, -0.0013),
    'sigma_0': (0.1035, 0.5998)
}
ONE_D_YLIM_RANGES = [
    [0, np.float64(706.2420646802517)],
    [0, np.float64(4.645092589303468)],
    [0, np.float64(38.86389292729265)],
    [0, np.float64(14.325739644737975)]]


@dataclasses.dataclass
class Result:
    posterior: np.ndarray
    truth: np.ndarray
    npts: int
    labels: list

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            posterior = pd.DataFrame(data['posterior']['content'])
            truths = data['injection_parameters']
            labels = list(truths.keys())
            npts = data['meta_data']['npts']
            truths = np.array([truths[label] for label in labels])
            posterior = posterior[labels].to_numpy()
            return cls(posterior=posterior, truth=truths, npts=npts, labels=labels)


def _get_round_number(filename):
    """Extract the round number from the filename."""
    return int(os.path.basename(filename).split('_')[0].split("round")[-1])




    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Merged PDF saved to {output_path}")
    # os.remove(pdf_path1)
    # os.remove(pdf_path2)

def _color_ax_to_white(ax):
    """
    Change all axes spines, ticks labels to white.
    """
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.tick_params(axis='both', colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')


from PIL import Image

def images_to_transparent_gif(image_paths, output_path, duration=200, loop=0):
    """
    Create an animated transparent GIF from a list of same-sized RGBA PNGs.

    Parameters:
    - image_paths: List of input PNG paths (with transparency).
    - output_path: Destination path for the GIF.
    - duration: Duration per frame in milliseconds.
    - loop: Number of loops (0 = infinite).
    """
    frames = [Image.open(p).convert("RGBA") for p in image_paths]

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        disposal=2,  # Use 'disposal=2' for transparency
    )
    print(f"GIF saved to {output_path}")
    print(f"✅ Transparent GIF saved to: {output_path}")

files = []

#
files = glob.glob(f'{HERE}/data/*.json')
files = sorted(files, key=lambda x: _get_round_number(x))
reference_result = Result.load(files[-1])



for f in tqdm(files, desc='Loading results'):
    result = Result.load(f)

    fig = plotGTC(
        chains=[result.posterior, reference_result.posterior],
        chainLabels=[
            f"$N={result.npts}$",
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
    axes = fig.get_axes()

    # change all axes spines, ticks labels to white
    for ax in axes:
        _color_ax_to_white(ax)

    # get all the diagonal axes (axes6,7,8,9) out of 10 axes
    axes = axes[6:10]
    # remove spines from the axes
    for i, ax in enumerate(axes):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='both', which='both', length=0)
        ax.set_ylim(*ONE_D_YLIM_RANGES[i])

    # set the xlabels
    fname_corner = f'{OUTDIR}/npts_{result.npts}_corner.png'
    fig.savefig(fname_corner, bbox_inches='tight', transparent=True, dpi=450)
    plt.close(fig)


    # plot 2 -- the JSD
    fname_jsd= f'{OUTDIR}/npts_{result.npts}_jsdiv.png'
    plt.figure(figsize=(2.7, 2))
    plt.plot(JSDIV['npts'], JSDIV['js'],  linestyle='-', color='lightgray')
    plt.scatter(result.npts, JSDIV.loc[JSDIV['npts'] == result.npts, 'js'], color='#c79af0', zorder=10)
    plt.xlabel('Number of points')
    plt.ylabel('JSD')
    # all axes spines, ticks labels to white
    ax = plt.gca()
    _color_ax_to_white(ax)

    plt.savefig(fname_jsd, bbox_inches='tight', transparent=True, dpi=300)
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



print(ONE_D_YLIM_RANGES)

# combine PDFs into a gif.
