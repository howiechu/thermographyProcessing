import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib import rc, font_manager
from scipy import interpolate, ndimage, signal
import copy
from customImports import plotparam
plotparam.update_params()
colors = plotparam.thermography_pastel

class thermography:
    '''
    Creates a battery object
    
    Parameters:
        array (nd.array): mat formatted video from ResearchIR/Atlas SDK
        cell (str): battery type; Kokam, A123, or custom
        realDim(list of int): real dimensions of active battery area in mm for non Kokam/A123 cells
    '''
    def __init__(self,  array, cell, *realDim):
        self.A = array
        self.cell = cell
        if cell in ['Kokam']:
            self.realDim = [200, 100]
        elif cell in ['A123']:
            self.realDim = [150, 200]
        elif cell in ['custom']:
            self.realDim = realDim
        else:
            raise Exception('Pick between Kokam/A123/custom + custom values')
    
    def plot_DAQ(self, arr, col, ylabel):
        '''
        Plots any any specified column of the DAQ file vs. time. Defaults to ambient temperature.
        
        Parameters:
            arr (nd.array): slightly processed data from DAQ (IVIUM or DT/Kepco)
            col (int): column number, not 0 (reserved for time series data)
            ylabel (str): y axis label
        
        Returns:
            a figure, basically a general plotter
        '''
        plt.close('figGen')
        figGen = plt.figure('figGen', figsize = (4,3))
        ax1 = plt.subplot2grid((1,1), (0,0))
        plt.plot(arr[:,0], arr[:,col], color = colors[0])
        ax1.set_xlabel('Time (sec)', fontname = ['Lato', 'Arial'])
        ax1.set_ylabel(ylabel, fontname = ['Lato', 'Arial'])
        plt.tight_layout()
    
    def plot_ROI(self, array1, array2, frame):
        '''
        Plots a specified frame of full video with battery area and ambient spot highlighted
        
        Parameters:
            array1 (list of ints): battery top right corner row, top right corner column, pixel height, pixel width
            array2 (list of ints): ambient spot top right corner row, top right corner column, pixel height, pixel width
            frame (int): frame to plot
        
        Returns:
            a figure with patches highlighting the regions of interest
        '''
        plt.close('figROI')
        figROI= plt.figure('figROI', figsize=(4,3))
        ax1 = plt.subplot2grid((1,1),(0,0))
        imROI = ax1.imshow(self.A[frame,:,:], cmap = 'magma', origin = 'upper')

        Batt = patches.Rectangle((array1[1],array1[0]),
            array1[3]-1,
            array1[2]-1,
            linewidth = 1,
            edgecolor = 'k',
            facecolor = 'none')
        ax1.add_patch(Batt)

        Amb = patches.Rectangle((array2[1],array2[0]),
            array2[3]-1,
            array2[2]-1,
            linewidth = 1,
            edgecolor = 'r',
            facecolor = 'none')
        ax1.add_patch(Amb)

        plt.title("Battery and Ambient Spot Regions", fontname = ['lato', 'arial'])
        plt.tight_layout()
            
    def extract_ROI(self, *arr):
        '''
        Slices out arrays from a bigger array (ROIs from full video)
        
        Parameters:
            arr (list of ints): list containing: [battery top left corner row, top left corner column, pixel height, pixel width]
        
        Returns:
            Generator that yields sliced out arrays
        '''
        for arrays in arr:
            sliced = self.A[:, arrays[0]:arrays[0]+arrays[2], arrays[1]:arrays[1]+arrays[3]]
            yield sliced
    
    def ambient_calibration(self, array1, array2):
        '''
        Subtracts the average value of array2 from every value of array1; 
        Used to subtract the surface average ambient spot temperature from every pixel in input array
        
        Parameters:
            array1 (nd.array): battery array
            array2 (nd.array): array that contains the ambient spot

        Returns:
            battery surface temperature as delta T
        '''
        for x in range(0,len(array2)):
            array1[x] = array1[x]-np.mean(array2[x])
        return array1
    
    def hotspot_location_array(self, array, startFrame, nFrames):
        '''
        Finds (x,y) of the hottest pixel in the array and stores it in a list and then averages both coordinates to give location
        
        Parameters:
            array (nd.array): battery array
            startFrame (int): frame that references t = 0
            nFrames (int): number of frames to average
        
        Returns:
            hot spot location
        '''
        indMax = []
        for x in range(startFrame,startFrame + nFrames):
            indMax.append(np.unravel_index(np.argmax(array[x-startFrame,...], axis=None), array.shape)[1:3])
            
        return np.array(indMax)
    
    def plot_extremes_tracker(self, battShape, hotLocArray, Ahot, Acold, patchSize):
        '''
        Plots the list of (x,y) coordinates and places a patch over the processed hot spot, also plots inputted cold spot coordinates
        
        Parameters:
            locIndex (list): list of x,y coordinates
            Ahot (list of int): pixel location of hot spot after post-processing of choice
            Acold (list of int): pixel location of cold spot
            patchSize (int): square dimension in pixels
        
        Returns:
            a figure shows hot spot evolution with a patch over given location
        '''

        plt.close('extremesTrack')
        figSpotTracker = plt.figure('extremesTrack', figsize = (4,3))
        ax1 = plt.subplot2grid((1,1),(0,0))
        imSpotTracker = ax1.scatter(hotLocArray[:,1]/battShape[1]*self.realDim[0],hotLocArray[:,0]/battShape[0]*self.realDim[1],
                                    c=np.arange(0,len(hotLocArray)),cmap='magma')

        hot = patches.Rectangle((Ahot[1]/battShape[1]*self.realDim[0], Ahot[0]/battShape[0]*self.realDim[1]),
            (patchSize-1)/battShape[1]*self.realDim[0],
            (patchSize-1)/battShape[0]*self.realDim[1],
            linewidth = 1,
            edgecolor = 'k',
            facecolor = 'none')
        ax1.add_patch(hot)

        cold = patches.Rectangle((Acold[1]/battShape[1]*self.realDim[0], Acold[0]/battShape[0]*self.realDim[1]),
            (patchSize-1)/battShape[1]*self.realDim[0],
            (patchSize-1)/battShape[0]*self.realDim[1],
            linewidth = 1,
            edgecolor = 'k',
            facecolor = 'none')
        ax1.add_patch(cold)
        
        ax1.set_facecolor('grey')
        plt.ylim([0,self.realDim[1]])
        plt.xlim([0,self.realDim[0]])
        plt.title('Hot/Cold spot', fontname = ['Lato', 'Arial'])
        plt.gca().invert_yaxis()
        plt.tight_layout()
        ax1.set_aspect((self.realDim[1]/self.realDim[0])/ax1.get_data_ratio())
    
    def plot_battery_ROI(self, arr, patchSize, frame, *roi):
        '''
        Plots a single frame with the hot/cold spot patch included
        
        Parameters:
            arr (nd.array): battery array
            Ahot (list of ints): x, y pixel coordinate of hot spot
            patchSize (int): pixel size of batch 
            frame (int): over which frame you want to show
        
        Returns:
            a figure that shows hotspot on top of a chosen frame of the IR video
        '''
        w = np.linspace(0, self.realDim[0], arr.shape[2])
        h = np.linspace(0, self.realDim[1], arr.shape[1])
        self.W, self.H = np.meshgrid(w, h)
        
        plt.close('hotspot')
        figHS = plt.figure('hotspot', figsize = (4,3))
        ax1 = plt.subplot2grid((1,1),(0,0))
        imBatt = ax1.pcolormesh(self.W, self.H, arr[frame,...], cmap = 'magma',
                                rasterized = True)
        plt.gca().invert_yaxis()
        cbar1 = figHS.colorbar(imBatt, orientation = 'horizontal')
        cbar1.set_label('$\mathregular{\Delta T(°C)}$', fontname = 'Lato')
        
        for rectangles in roi:
            patched = patches.Rectangle((rectangles[1]/arr[0].shape[1]*self.realDim[0],
                                        rectangles[0]/arr[0].shape[0]*self.realDim[1]),
                                       (patchSize-1)/arr[0].shape[1]*self.realDim[0],
                                       (patchSize-1)/arr[0].shape[0]*self.realDim[1],
                                       linewidth = 1,
                                       edgecolor = 'k',
                                       facecolor = 'none')
            ax1.add_patch(patched)
        
        plt.title('Battery ROI: '+str(frame), fontname = ['Lato', 'Arial'])
        plt.tight_layout()
        ax1.set_aspect((self.realDim[1]/self.realDim[0])/ax1.get_data_ratio())
        
    def extract_data(self, arr, Ahot, Acold, patchSize):
        '''
        Generates the hot spot, average, and cold spot area temperatures, usually averaged
        
        Parameters:
            arr (nd.array): battery array
            Ahot (list of ints): x, y pixel coordinate of hot spot
            patchSize (int): dimension of spot to average over
            
        Returns:
         Thot, Tavg, Tcold 
        '''
        
        Thot = np.empty(arr.shape[0])
        Tavg = np.empty(arr.shape[0])
        Tcold = np.empty(arr.shape[0])
        
        for x in range(0, arr.shape[0]):
            Thot[x] = np.array(np.mean(arr[x,Ahot[0]:Ahot[0]+patchSize,Ahot[1]:Ahot[1]+patchSize]), dtype=np.float64)
            Tavg[x] = np.array(np.mean(arr[x], dtype=np.float64))
            Tcold[x] = np.array(np.mean(arr[x, Acold[0]:Acold[0]+patchSize, Acold[1]:Acold[1]+patchSize]), dtype=np.float64)
        
        return Thot, Tavg, Tcold
    
    def plot_processed_thermography(self, Table, endTime, adjustable = True, figName = 'figOutput'):
        '''
        Plots the processed Thot, Tavg, Tcold, Voltage data
        
        Parameters:
            Table (nd.array): fully processed data array
            endTime (int): where to cut off data (used if you want to plot full charge/discharges where experimental time is much shorter)
            adjustable (boolean): interactive widget if true, false for fixed aspect, good for saving 
            
        Returns:
            1 x 2 figure of temperature and voltage data vs. time
        '''
        
        plt.close(str(figName))
        figOutput = plt.figure(str(figName), figsize = (6,3))
        ax1 = plt.subplot2grid((1,2),(0,0))
        for x in range(1,4):
            ax1.plot(Table[:,0], Table[:,x], color = colors[x-1])
        ax1.set_xlabel('Time (sec)', fontname = ['Lato', 'Arial'])
        ax1.set_ylabel('Temperature ($^{\circ}$C)', fontname = ['Lato', 'Arial'])
        plt.ylim([min(Table[:,3])-0.75,max(Table[:,1])+0.75])
        plt.xlim([-50, endTime])
        
        ax2 = plt.subplot2grid((1,2),(0,1))
        ax2.plot(Table[:,0], Table[:,4], color = colors[1])
        ax2.set_xlabel('Time (sec)', fontname = ['Lato', 'Arial'])
        ax2.set_ylabel('Potential (V)', fontname = ['Lato', 'Arial'])
        plt.ylim([min(Table[:,4])-0.05,max(Table[:,4])+0.05])
        plt.xlim([-50, endTime])
        
        if adjustable == True:
            pass
        else:
            ratio = 1.0
            for ax in [ax1, ax2]:
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                ax.set_aspect(abs((xmax-xmin)/(ymax-ymin))*ratio, adjustable='box')
        
        plt.tight_layout()
        
    def analyze_jumps(self, Table, dataSeries = 1, peakHeight = 0.1):
        '''
        Analyzes the jumps in the temperature data that is caused by fast occuring camera recalibrations
        
        Parameters:
            Table (nd.array): processed data array containing Time, Thot, Tavg, Tcold
            dataSeries (int): 1 for hot, 2 for avg, 3 for cold, defaults to cold for no reason
            peakHeight (float): height to be considered a peak that needs to be fixed
        
        Returns:
            Figures containing the diff'd temperatures along with the peak locations where the fixes will be applied
        '''
        self.diff = {}
        for i in range(1,4):
            self.diff[i] = np.diff(Table[:,i])
        self.peaks,_ = signal.find_peaks(np.absolute(self.diff[dataSeries]), peakHeight)
        
        plt.close('dataJumps')
        figDiff = plt.figure('dataJumps', figsize = (9,3))
        for i,title in zip(range(1,4), ['dThot', 'dTavg', 'dTcold']):
            plt.subplot2grid((1,3),(0,i-1))
            plt.plot(self.diff[i], color = colors[2])
            plt.plot(self.peaks, self.diff[i][self.peaks], 'x', ms = 10, color = colors[0])
            plt.title(title, fontname = ['Lato', 'Arial'])
    
    def execute_jumps(self, Table):
        '''
        Executes the fixing procedure based off of the results from analyze_jumps; 
        subtracts out the jumps from the peak location +1 to the end iteratively, stepping through all the peaks
        
        Parameters: 
            Table(nd.array): processed data array containing Time, Thot, Tavg, Tcold
        
        Returns:
            Manipulated Table array
        '''
        altTable = copy.deepcopy(Table)
        for j in [1,2,3]:
            for i in range(len(self.peaks)):
                altTable[self.peaks[i]+1:,j] = Table[self.peaks[i]+1:,j] - self.diff[j][self.peaks[i]]
        return altTable
    
    def plot_video_frames(self, arr, times, nCol, figName = 'thermograms'):
        '''
        Plots various time frames of input array, figure auto expands based off of number of wanted columns
        
        Parameters:
            arr (nd.array): video array 
            times (list of ints): desired time slots for plotting
            nCol (int): number of columns for subplots
            figName (str, optional): name for referencing the matplotlib figure
            haha fuck you kirk
        
        Returns:
            a figure with subplots of thermograms and select time steps
        '''
        
        rows = int(np.floor(len(times)/nCol))
        if len(times) % nCol != 0:
            rows = rows + 1

        nPlots = len(times)
        vmin = np.amin(arr)
        vmax = np.amax(arr)
        plt.close(str(figName))
        figOutput = plt.figure(str(figName), figsize = (nCol*3.3, rows*3.2))
        
        r = 0
        while nPlots > 0 and r < rows:
            c = 0
            while nPlots > 0 and c < nCol:
                ax = plt.subplot2grid((rows, nCol),(r,c))
                ax.axis('off')
                ax.invert_yaxis()
                cax = ax.pcolormesh(self.W, self.H, arr[times[nPlots*-1]],
                                    cmap='magma', vmin = vmin, vmax = vmax,
                                    rasterized=True)
                CS = ax.contour(self.W, self.H, arr[times[nPlots*-1]], np.arange(vmin, vmax, 0.2),
                                cmap = 'magma_r', linewidths = 1)
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                ax.set_aspect(abs((xmax-xmin)/(ymax-ymin))*0.5, adjustable='box')
                plt.clabel(CS, CS.levels, fmt = '%1.1f', fontsize = 10)
                cbar = figOutput.colorbar(cax,
                                          ticks = np.arange(np.floor(vmin), np.ceil(vmax), 1),
                                          orientation = 'horizontal')
                cbar.set_label('$\mathregular{T(^{\circ}C)}$', fontname = 'Lato')
                ax.set_title('{} s'.format(times[nPlots*-1]), fontname = 'Lato')
                c += 1
                nPlots = nPlots - 1
            r +=1
        plt.tight_layout()