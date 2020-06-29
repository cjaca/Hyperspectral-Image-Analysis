import rasterio  # read and process rasters
import numpy  # matrices
import tkinter  # gui

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox  # diplsay messages in UI

# UI

class Root(tkinter.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("SAM")
        self.labelFrame1 = ttk.LabelFrame(self, text="1.Open A File")  # function1
        self.labelFrame1.grid(column=0, row=1, padx=10, pady=30)

        self.labelFrame2 = ttk.LabelFrame(self, text="2.Display TCC&FCC")  # function2
        self.labelFrame2.grid(column=12, row=1, padx=10, pady=30)

        self.button1()
        self.button2()

    def button1(self):
        self.button1 = ttk.Button(self.labelFrame1, text="Browse a File", command=self.fileDialog)
        self.button1.grid(column=1, row=1)

    def fileDialog(self):  # readfile
        self.filename = filedialog.askopenfilename(initialdir="\\", title="Select a File",
                                                   filetype=(("tiff", "*.tif"), ("All Files", "*.*")))
        self.label = ttk.Label(self.labelFrame1, text="")
        self.label.grid(column=1, row=2)

        self.num_of_dir_till_file = len(self.filename.split("/"))
        self.just_file_name = self.filename.split("/")[self.num_of_dir_till_file - 1]

        self.label.configure(text="Selected : " + self.just_file_name)

    def button2(self):
        self.button2 = ttk.Button(self.labelFrame2, text="Show TCC&FCC", command=self.fun1)
        self.button2.grid(column=3, row=4)

    def fun1(self):

        # for drawing images
        import matplotlib.pyplot as plt

        raster = rasterio.open(self.filename, 'r')

        # read image with band
        # Read the grid values into numpy arrays
        nir = raster.read(4)
        red = raster.read(3)
        green = raster.read(2)
        blue = raster.read(1)

        # normalize the grid values
        def normalize(data):
            """Normalizes numpy arrays into scale 0.0 - 1.0"""
            array_min = data.min()
            array_max = data.max()

            return ((data - array_min) / (array_max - array_min))
            # return new_array


        # normalise the bands
        nirn = normalize(nir)
        redn = normalize(red)
        greenn = normalize(green)
        bluen = normalize(blue)

        # Create TCC
        rgb = numpy.dstack((redn, greenn, bluen))
        # Create FCC
        nrg = numpy.dstack((nirn, redn, greenn))

        plt.figure(1)
        plt.imshow(rgb)
        messagebox.showinfo("Information",
                            "Please Select reference points on the FCC(figure 2) by double click and close the User Interface and wait")

        #######to read refernce pixel coordinates
        self.ref_count = 0
        plt.figure(2)
        ref_cord = []
        ax = plt.gca()
        fig = plt.gcf()
        implot = ax.imshow(nrg)

        def onclick(event):
            if event.dblclick:  # read data on double click
                if event.xdata != None and event.ydata != None:
                    ref_cord.append([round(event.xdata), round(event.ydata)])
                    self.ref_count
                    self.ref_count = self.ref_count + 1

        cid = fig.canvas.mpl_connect('button_press_event', onclick)

        plt.show()

        # default palettte made to classsify
        class_color = {0: [255, 0, 0], 1: [0, 255, 0], 2: [0, 0, 255], 3: [255, 0, 255], 4: [0, 200, 200],
                       5: [200, 200, 0], 6: [100, 100, 0], 7: [250, 255, 80], 8: [200, 0, 100], 10: [0, 0, 0]}

        with rasterio.open(self.filename, 'r') as ds:
            arr = ds.read()
            ix = max(ds.height, ds.width)
            iy = min(ds.width, ds.height)

            bands = arr.shape[0]

            arr = numpy.array(arr, dtype=numpy.float64)


        # ref_vect is refernce pixel
        ref_vect = [[0 for x in range(bands)] for y in range(self.ref_count)]

        for i in range(self.ref_count):
            for j in range(bands):
                ref_vect[i][j] = arr[j, int(ref_cord[i][1]), int(ref_cord[i][0])]

        c = numpy.ndarray((ix, iy, 3))

        for x in range(ix):
            for y in range(iy):
                p_ang = [0] * self.ref_count
                for j in range(self.ref_count):

                    p_mag = [0] * self.ref_count
                    product_numtr = [0] * self.ref_count
                    p_deno = [0] * self.ref_count
                    p_r = [0] * self.ref_count
                    p_reno = [0] * self.ref_count
                    p_cos = [0] * self.ref_count

                    for nb in range(bands):
                        t = arr[nb, x, y]
                        r = ref_vect[j][nb]
                        product_numtr[j] += (t * r)
                        p_r[j] += (r * r)
                        p_mag[j] += (t * t)

                    p_deno[j] = (numpy.sqrt(p_mag[j]))
                    p_reno[j] = (numpy.sqrt(p_r[j]))
                    p_cos[j] = product_numtr[j] / (p_deno[j] * p_reno[j])

                    p_ang[j] = numpy.arccos(p_cos[j])

                if min(p_ang) < 0.1:
                    class_no = numpy.argmin(p_ang, axis=0)
                else:
                    class_no = 10
                c[x, y] = class_color[class_no]

        plt.imshow(c)
        plt.show()

        f, axarr = plt.subplots(1, 3)
        axarr[0].imshow(rgb)
        axarr[0].set_title('TCC')
        axarr[1].imshow(nrg)
        axarr[1].set_title('FCC')
        axarr[2].imshow(c)
        axarr[2].set_title('Classified')
        plt.show()


if __name__ == '__main__':
    root = Root()
    root.mainloop()
