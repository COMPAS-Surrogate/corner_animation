from custom_corner import plot_custom_corner
from utils import Result, HERE, RANGES, LATEX
import matplotlib.pyplot as plt

JEFF_FNAME = "round25_675pts_highres_result.json"
AVI_FNAME = "round25_675pts_variable_lnl_result.json"

DIR = f"{HERE}/data2/"
DIRS = [
    f"{DIR}/out_22/",
    f"{DIR}/out_99/",
]


def plot_comparison(d):
    jeff_fname = f"{d}/{JEFF_FNAME}"
    avi_fname = f"{d}/{AVI_FNAME}"
    jeff_result = Result.load(jeff_fname)
    avi_result = Result.load(avi_fname)
    fig = plot_custom_corner(
        chains=[
            avi_result.posterior,
            jeff_result.posterior,

        ],
        chainLabels=[
            f"LnL Surrogate (N=${avi_result.npts}$)",
            f"Jeff+Mandel '23 Model",
        ],
        truths=[jeff_result.truth],
        colorsOrder=['purples', 'greens'],
        # paramRanges=[RANGES[l] for l in jeff_result.labels],
        paramNames=[LATEX[l] for l in jeff_result.labels],
        figureSize='AandA_page',
        customLegendFont=dict(size=15)
    )


    fig.savefig(f"{d}/corner.png", bbox_inches='tight',  dpi=450)
    plt.close(fig)


for d in DIRS:
    plot_comparison(d)
