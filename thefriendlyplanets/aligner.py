#!/usr/bin/env python

# import all the tools we'll need
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import sys, os

# astropy tools
from astropy.io.fits import open
from astropy.stats import SigmaClip
from astropy.visualization import simple_norm
from astropy.time import Time

# more complicated background treatment?
# from photutils.background import Background2D, MedianBackground

from IPython.display import display
from ipywidgets import Output
from IPython import get_ipython

is_notebook = get_ipython().__class__.__name__ == "ZMQInteractiveShell"
if is_notebook:
    get_ipython().run_line_magic("matplotlib", "notebook")
else:
    plt.ion()

from scipy.ndimage import median_filter

# define an object that will align one image
class make_friendly_image:
    """
    Define an object for interactively selecting the center
    of an image and creating a zoomed-in stamp around it,
    with a standardized processing and visualization scales.
    """

    def __init__(
        self,
        filename,
        size=256,
        planet_name="Uranus",
        arcseconds_per_pixel=0.32,
        vmin=1,
        vmax=1e3,
        filter_pixels=5,
        cmap="gray_r",
        suffixes=["pdf", "png"],
        row=None,
        col=None,
    ):
        """
        Initialize by loading an image,
        displaying it in an interactive window,
        prompting the user for input, and then
        waiting for a center to be selected.

        Parameters
        ----------
        filename : str
            The filaname of the FITS file image to load.
        size : int
            The half-width of a zoom box, meaning that the
            total width of the zoom box is twice this number.
        planet_name : str
            The name of the planet, for titles and filenames.
        arcseconds_per_pixel : float
            The pixel scale, in arcsecounds/pixel.
            If None, the axes will be shown in pixels.
        vmin, vmax:
            The min and max values for the colormap
        """

        # store some attributes to hang onto
        self.filename = filename
        self.size = size
        self.center = ()
        self.planet_name = planet_name
        self.arcseconds_per_pixel = arcseconds_per_pixel
        self.vmin, self.vmax = vmin, vmax
        self.filter_pixels = filter_pixels
        self.cmap = cmap
        self.suffixes = suffixes

        # load the image
        self.read()

        self.already_provided = (row is not None) and (col is not None)
        if self.already_provided:
            self.center = (row, col)
            print(f"⌨️ You provided a center of {self.center}")

        # display the image
        self.display_with_zoom()

        if self.already_provided:
            self.update_zoom()
            self.save_zoom()

    def speak(self, x):
        if is_notebook:
            with self.output:
                print(x)
        else:
            print(x)

    def read(self):
        """
        Load the image stored in self.filename.
        """

        # open the FITS image
        hdu = open(self.filename)

        # for SBO, the 0th extension has everything
        self.image, self.header = hdu[0].data, hdu[0].header

        # make an initial guess to center at the image's center
        initial_row = int(self.image.shape[0] / 2)
        initial_col = int(self.image.shape[1] / 2)
        self.center = (initial_row, initial_col)

    def tidy(self, i):
        """
        A quick kludge to help display images better.
        It will do an approximate background subtraction
        and apply a median filter to eliminate most
        cosmic rays or weird hot pixels.
        """

        # estimate the background simply as the image's median
        background = np.median(i)

        # apply median filter to get rid of outliers and reduce noise
        tidied = median_filter(i - background, size=self.filter_pixels)

        # return the tidied image
        return tidied

    def imshow(self, image, ax=None, **kw):
        """
        A helper to make sure that we display all
        images in the same way, with the same colorbar.

        Parameters
        ----------
        image : np.array
            The image to display
        ax : matplotlib.pyplot.Axes
            The ax into which to put the image
        kw : dict
            Extra keyword arguments will be passed to imshow
        """

        # make sure there's a place to plot into
        if ax is None:
            ax = plt.gca()

        # set an image normalization
        norm = simple_norm(image, "asinh", min_cut=1, max_cut=1e3)

        plt.sca(ax)
        return plt.imshow(image, origin="lower", norm=norm, cmap=self.cmap, **kw)

    def display_with_zoom(self):
        """
        Create a two-panel figure,
        showing the whole image and
        a zoom in on the chosen center.
        """
        if is_notebook:
            self.output_for_plots = Output()
            display(self.output_for_plots)

            self.output = Output()
            display(self.output)

        def make_the_plots():
            # create figure with two axes in it
            self.fi, self.ax = plt.subplots(
                1, 2, figsize=(8, 4), dpi=100, gridspec_kw=dict(width_ratios=[1, 0.5])
            )

            # display the full image
            tidied_full = self.tidy(self.image)
            self.imshow(tidied_full, ax=self.ax[0])

            # display the zoom
            self.setup_zoom()

            if self.already_provided == False:
                # ask the user to click on a center
                self.setup_adjust_center()

        if is_notebook:
            with self.output_for_plots:
                make_the_plots()
        else:
            make_the_plots()

    def create_stamp(self):
        """
        Cut out a stamp around the chosen center.
        """
        if self.center is not None:
            row, col = self.center
            size = self.size
            stamp = self.image[(row - size) : (row + size), (col - size) : (col + size)]
            return stamp
        # FIX ME, this'll break for something too near the edge of the image

    def setup_zoom(self):
        """
        Setup the zoomed-in image display for the first time.
        """

        self.speak(f"🌌 Displaying image '{self.filename}'.")

        plt.sca(self.ax[1])
        stamp = self.create_stamp()
        tidied_stamp = self.tidy(stamp)
        s = self.size * self.arcseconds_per_pixel
        self.zoomed_imshow = self.imshow(
            tidied_stamp, ax=self.ax[1], extent=[-s, s, -s, s]
        )
        lkw = dict(color="white", alpha=0.3, linewidth=2)
        plt.axvline(0, **lkw)
        plt.axhline(0, **lkw)
        t = Time(self.header["DATE-OBS"])
        label = f"{t.iso[:-7]} UT"
        plt.title(f"{self.planet_name}\n{label}\nJD={t.jd:.2f} days")
        plt.grid()

    def update_zoom(self):
        """
        Update an existing zoomed-in image display.
        """

        # with self.output:
        #    print(f"✨ You centered on {self.center}.")
        stamp = self.create_stamp()
        tidied_stamp = self.tidy(stamp)
        self.zoomed_imshow.set_data(tidied_stamp)
        self.ax[0].set_title(f"centered at (row, col) = {self.center}")
        plt.draw()

    def setup_adjust_center(self):
        """
        Tell the figure to pay attention to clicks.
        """
        self.cid_button = self.fi.canvas.mpl_connect(
            "button_press_event", self.__onclick__
        )
        self.cid_key = self.fi.canvas.mpl_connect("key_press_event", self.__onkey__)

        # with self.out_text:
        if self.already_provided == False:
            self.speak(
                """🪐 Please try to center your planet:
            Double click at the planet's center.
            (You can use the plot's zoom to get closer.)
            Press the arrow keys to nudge the center.
            Type `s` or `enter` to save and quit."""
            )

    def save_zoom(self):
        """
        Save out the final image.
        """

        if self.already_provided == False:
            self.fi.canvas.mpl_disconnect(self.cid_button)
            self.fi.canvas.mpl_disconnect(self.cid_key)

        # create a new figure for saving the plot
        this_figure = plt.figure(figsize=(5, 5))

        # create and tidy the stamp
        stamp = self.create_stamp()
        tidied_stamp = self.tidy(stamp)

        # imshow the stamp
        s = self.size * self.arcseconds_per_pixel
        self.imshow(tidied_stamp, extent=[-s, s, -s, s])

        # add title
        t = Time(self.header["DATE-OBS"])
        label = f"{t.iso[:-7]}"
        plt.title(f"{self.planet_name}\n{label} UT | JD={t.jd:.3f} days")

        # set the aspect ratio to be equal in both dimensions
        plt.axis("equal")

        # add a grid
        plt.grid(color="gray", alpha=0.3)

        # add x + y labels
        plt.xlabel("x (arcseconds)")
        plt.ylabel("y (arcseconds)")

        fileprefix = f'{self.planet_name.lower()}-{2*self.size}px-{label.replace(" ", "-").replace(":", "")}'

        x = "+".join(self.suffixes)
        self.speak(f"💾 Saving image(s) to '{fileprefix}.{x}'")
        self.speak(f"🤩 All done!")
        for suffix in self.suffixes:
            plt.savefig(f"{fileprefix}.{suffix}", dpi=300)

        plt.close(this_figure)
        # close the interactive figure
        plt.close(self.fi)

    def __onkey__(self, event):
        row, col = self.center
        k = event.key.lower()
        if k == "left":
            col -= 1
        if k == "right":
            col += 1
        if k == "down":
            row -= 1
        if k == "up":
            row += 1
        if k in "s" or k == "enter":
            self.save_zoom()
            return
        self.center = (row, col)
        self.update_zoom()

    def __onclick__(self, event):
        if event.dblclick:
            row, col = int(event.ydata), int(event.xdata)
            self.center = (row, col)
            self.speak(f"🐭 You double-clicked at {self.center}")
            self.update_zoom()

        return self.center


def align_list(filepath):
    files = glob(filepath)
    for f in files:
        FriendlyImage(f, size=256).display_with_zoom()


if __name__ == "__main__":
    filepath = sys.argv[1]
    align_list(filepath)
