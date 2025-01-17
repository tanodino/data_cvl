import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
import sys
from sklearn.utils import shuffle
import os


def subsampleData(data, groups, labels, max_value=50000):
    new_data = []
    new_groups = []
    new_labels = []
    print(np.unique(labels))
    for v in np.unique(labels):
        print("\tanalysing class %d"%v)
        idx = np.where(labels == v)[0]
        temp_data = data[idx]
        temp_groups = groups[idx]

        temp_data, temp_groups = shuffle(temp_data, temp_groups)
        
        temp_data = temp_data[0:max_value]
        temp_groups = temp_groups[0:max_value]
        
        new_data.append( temp_data )
        new_groups.append( temp_groups )
        new_labels.append( np.ones(temp_data.shape[0])*v  )
    
    return np.concatenate(new_data, axis=0), np.concatenate(new_groups, axis=0), np.concatenate(new_labels, axis=0)

def getDataIdx(objs, groups):
    data_idx = []
    for obj_id in objs:
        idx = np.where(groups == obj_id)[0]
        data_idx.append( idx )
    return np.concatenate(data_idx,axis=0)

hash_merge = {1:1, 2:2, 3:3, 4:4, 5:5, 6:5, 7:5, 8:5, 9:5, 11:6, 15:7, 16:7, 17:8, 18:8, 19:8, 20:9, 22:9, 24:9, 25:9, 28:9}
#hash_merge = {1:1, 2:2, 3:3, 4:4, 5:5, 6:5, 7:5, 8:5, 11:6, 16:7, 17:8, 18:8, 19:8, 20:9, 24:9, 25:9, 28:9}

year = int(sys.argv[1])

#output_folder = "splits_%d"%year
output_folder = "splits_%d_v2"%year
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


print("loading GT")
gt_data_fileName = "gt_data_%d.npy"%year
group_data_fileName = "pid_data_%d.npy"%year
gt = np.load(gt_data_fileName)
print("GT loaded")
print("loading DATA")
data_fileName = "data_%d.npy"%year
data = np.load(data_fileName)
print("DATA loaded")

groups = gt[:,3]
labels = gt[:,2]
labels = [hash_merge[l] for l in labels]
labels = np.array(labels)

max_samples_per_class = 5000

print("START DATA SUBSAMPLE")
data, groups, labels = subsampleData(data, groups, labels, max_value=max_samples_per_class)
print("END DATA SUBSAMPLE")

np.save(output_folder+"/"+gt_data_fileName, labels)
np.save(output_folder+"/"+data_fileName, data)
np.save(output_folder+"/"+group_data_fileName, groups)



train_perc = .5
valid_perc = .2
n_repeated_hold_out = 5

for i in range(n_repeated_hold_out):
    print("hold out %d"%i)
    data, groups, labels = shuffle(data, groups, labels)
    lab2objs = {}
    train_objs_ids = []
    valid_objs_ids = []
    test_objs_ids = []
    for l in np.unique( labels ):
        idx = np.where(labels == l)[0]
        obj_idx = shuffle( np.unique( groups[idx] ), random_state=i*100 )
        n_objs = len(obj_idx)
        limit_train = int(train_perc * n_objs)
        limit_valid = int((train_perc+valid_perc) * n_objs)
        train_objs_ids.append( obj_idx[0:limit_train] )
        valid_objs_ids.append( obj_idx[limit_train:limit_valid])
        test_objs_ids.append( obj_idx[limit_valid::] )

    train_objs_ids = np.concatenate(train_objs_ids)
    valid_objs_ids = np.concatenate(valid_objs_ids)
    test_objs_ids = np.concatenate(test_objs_ids)

    train_objs_ids = np.unique(train_objs_ids)
    valid_objs_ids = np.unique(valid_objs_ids)
    test_objs_ids = np.unique(test_objs_ids)

    train_idx = getDataIdx(train_objs_ids, groups)
    valid_idx = getDataIdx(valid_objs_ids, groups)
    test_idx = getDataIdx(test_objs_ids, groups)

    np.save(output_folder+"/train_data_%d_%d.npy"%(i,year), data[train_idx])
    np.save(output_folder+"/train_label_%d_%d.npy"%(i,year), labels[train_idx])

    np.save(output_folder+"/valid_data_%d_%d.npy"%(i,year), data[valid_idx])
    np.save(output_folder+"/valid_label_%d_%d.npy"%(i,year), labels[valid_idx])

    np.save(output_folder+"/test_data_%d_%d.npy"%(i,year), data[test_idx])
    np.save(output_folder+"/test_label_%d_%d.npy"%(i,year), labels[test_idx])