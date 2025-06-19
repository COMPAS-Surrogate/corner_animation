import glob
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
    # os.remove(img_path1)
    # os.remove(img_path2)


HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'out')
os.makedirs(OUTDIR, exist_ok=True)


LATEX = dict(
    aSF=r'$a_\mathrm{SF}$',
    dSF=r'$d_\mathrm{SF}$',
    mu_z=r'$\mu_z$',
    sigma_0=r'$\sigma_0$'
)



RANGES = {
    'aSF': (0.005, 0.015),
    'dSF': (4.2, 5.2),
    'mu_z': (-0.4931, -0.0013),
    'sigma_0': (0.1035, 0.5998)
}


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
    # make background semi transparent
    ax.set_facecolor((0, 0, 0, 0.4))  # RGBA with alpha for transparency



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
