import rasterio as rio
import sys
import os
import numpy as np

#5

def extractGTperDate(gt_dir_poly, gt_dir_class, year):
    gt_classes = getRaster(gt_dir_class)
    gt_poly = getRaster(gt_dir_poly)
    classes_id = np.unique(gt_classes)
    classes_id = classes_id[classes_id!=0]
    print(np.unique(classes_id))
    data = []
    for el in classes_id:
        idx = np.where(gt_classes == el)
        len_idx = len(idx[0])
        temp_cl = np.ones(len_idx) * el
        temp_poly = gt_poly[idx]
        temp_data = np.stack([idx[0],idx[1],temp_cl, temp_poly],axis=1)
        data.append(temp_data)
    data = np.concatenate(data,axis=0)
    np.save("gt_data_%d_spatioTemporal.npy"%year,data)


def getRaster(fileName):
    src = rio.open(fileName)
    band = src.read(1)
    src.close()
    return band

year = int(sys.argv[1])



#gt_dir_poly = gt_dir+"/polygon_ID_20px_expand.tif"


#for year in [2018,2021]:
gt_dir ="GT_%d_spatioTemporal"%year
gt_dir_class = gt_dir+"/gt_clID.tif"
gt_dir_poly = gt_dir+"/gt_pID.tif"
extractGTperDate(gt_dir_poly, gt_dir_class, year)


    