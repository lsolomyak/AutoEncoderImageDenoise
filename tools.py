import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import log10

def scale(data):
    #Scaling the data between 0 and 1 before it goes into the network
    scalars = []
    s1,s2,s3,s4 = data.shape    
    data = data.reshape(s1*s2,s3,s4)
    scaled_data = np.zeros_like(data)
    for i in range(s1*s2):
        scalars.append(np.max(np.abs(data[i,:,:])))
        scaled_data[i,:,:] = ((data[i,:,:]/scalars[i])/2)+0.5
    scaled_data = scaled_data.reshape(s1,s2,s3,s4)
    return scaled_data, scalars


def inv_scale(scaled_data,scalars):
    s1,s2,s3,s4 = scaled_data.shape   
    scaled_data = scaled_data.reshape(s1*s2,s3,s4)
    # returning data to its original amplitude
    orig_data = np.zeros_like(scaled_data)
    for i in range(s1):
        orig_data[i,:,:] = ((scaled_data[i,:,:]-0.5)*2)*scalars[i]
    
    orig_data = orig_data.reshape(s1,s2,s3,s4)
    return orig_data

def add_noise(data, noise_level):
    """Adding gaussian noise to the data
        Inputs: list of arrays of data
                noise level of gaussian noise you want added"""
    noise = noise_level*np.random.normal(loc=0,scale=1.0,size=data.shape)
    data = data + noise

    data = np.clip(data,0,1)

    return data,noise

def plot_results(data,start=0,save=False):
    """Input: a list of variables containing MNIST data to plot
              what number in the data you want to start at"""
    
    n = 10
    if start == None:
        start=0
    plt.figure(figsize=(20,len(data)*2))
    # Looping over datasets to compare
    for j in range(len(data)):
        # Looping over numbers in each dataset
        for i in range(start,start+n):
             loc = i-start
             ax = plt.subplot(len(data),n,loc+1+(j*n))
             plt.imshow(data[j][i])
             plt.gray()
             ax.get_xaxis().set_visible(False)
             ax.get_yaxis().set_visible(False)

    if save:
        file_name = input("file name:")
        plt.savefig('./results/images/%s_start%s.png'%(file_name,start))

def store_hist(global_hist,recent_hist,name): 
    """ Input :     Overall history for all models (dataframe)
                    recent model run history (dataframe)
                    name for most recent model (string)
        Output:     Overall history for all models (dataframe) 

    """
    # Removing previous run of this model from model_hist
    global_hist = global_hist[global_hist.model != name]
    recent_hist["model"] = name
    global_hist = pd.concat([global_hist,recent_hist],axis=0)

    return global_hist

# Creating a function to efficiently plot and compare the different models I'm testing
def plot_perf(hist,models,metrics):
    """
    Input: 
        models - list of strings of which models you want to compare, default is all
        metrics - list of strings of which metrics you want to compare"""

    # If empty list passed, all models are compared
    if len(models) == 0: 
        models=list(hist["model"].unique())   
    plt.figure(figsize=(12,6))
    # Looping through all models and metrics and plotting them on the graph with appropriate labels
    for model in models:
        for m in metrics:
            y_plt = hist[(hist["model"]==model)][m].values
            x_plt = range(0,len(y_plt))
            plt.plot(x_plt,y_plt,linewidth=3,label=model+' ('+m+')')
    plt.xlabel('Epochs')
    plt.ylabel(m)
    plt.legend()

    # def img2windows(arr, nrows, ncols):
def img2windows(arr,nrows,ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h,w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))


def windows2img(arr, h, w):
    """
    Return an array of shape (h, w) where
    h * w = arr.size

    If arr is of shape (n, nrows, ncols), n sublocks of shape (nrows, ncols),
    then the returned array preserves the "physical" layout of the sublocks.
    """
    n, nrows, ncols = arr.shape
    return (arr.reshape(h//nrows, -1, nrows, ncols)
               .swapaxes(1,2)
               .reshape(h, w))

def PSNR(clean, noisy): 
    mse = np.mean((clean - noisy) ** 2) 
    if(mse == 0):  # MSE is zero means no noise is present in the signal . 
                  # Therefore PSNR have no importance. 
        return 100
    max_pixel = np.max(noisy)
    psnr = 20 * log10(max_pixel / np.sqrt(mse)) 
    return psnr


def pred_resh(data,output_size,num_wind,wind_size):

    # Reshaping predictions
    data_resh= data.reshape(int(data.shape[0]/num_wind),num_wind,wind_size,wind_size)

    img = []

    for iImg in range(data_resh.shape[0]):
        img.append(windows2img(data_resh[iImg],output_size,output_size))

    img = np.array(img)


    return img

def inp_resh(data,wind_size):

    # Splitting images into windows to pass through the autoencoder if we're using windows 
    windows = []

    win_size = 32
    for iImg in range(data.shape[0]):
        windows.append(img2windows(data[iImg,:,:,0],win_size,win_size))

    windows = np.array(windows)
    return windows
