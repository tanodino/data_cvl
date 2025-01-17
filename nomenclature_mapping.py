import pandas as pd
import geopandas as gpd
import numpy as np
import sys
#original_code
# HCAT2_code
# HCAT3_code
#2018

# Read the CSV file
mapping_data_1 = pd.read_csv("fr_2018_eurocrops.csv")
mapping_data_2 = pd.read_csv("fr_other_years.csv")

mapping_data = pd.concat([mapping_data_1, mapping_data_2])
#original_code
#HCAT2_code
#OR
#HCAT3_code
orig_code = mapping_data['original_code'].to_numpy()
HCAT_code = mapping_data['HCAT2_code'].to_numpy()
hash_mapping = {}
for i, val in enumerate(orig_code):
    hash_mapping[val] = HCAT_code[i]

#for v in hash_mapping.keys():
#    print("%s %s"%(v,hash_mapping[v]))

#exit()

# View the first 5 rows
#print(data['original_code'])


year = int(sys.argv[1])

#data = gpd.read_file("GT_%d/gt.shp"%year)
data = gpd.read_file("GT_%d_spatioTemporal/gt.shp"%year)


code_cultu = data['CODE_CULTU'].to_numpy()
code_group = data['CODE_GROUP'].to_numpy()
area = data.area.to_numpy()
hashCG2Area = {}

data = data[data.is_valid]

for index, poi in data.iterrows():
    val = data.loc[index, 'CODE_GROUP']
    val = int(val)
    if val not in hashCG2Area:
        hashCG2Area[val] = 0
    hashCG2Area[val]+=data.loc[index,'geometry'].area

for v in sorted(hashCG2Area.keys()):
    print("CG %d Surface %.2f"%(v, int(hashCG2Area[v]/100) ))

hash_merge = {1:1, 2:2, 3:3, 4:4, 5:5, 6:5, 7:5, 8:5, 9:5, 11:6, 15:7, 16:7, 17:8, 18:8, 19:8, 20:9, 22:9, 24:9, 25:9, 28:9}

hashMerge2Area = {}
for v in sorted(hashCG2Area.keys()):
    if hash_merge[v] not in hashMerge2Area:
        hashMerge2Area[hash_merge[v]] = 0
    hashMerge2Area[hash_merge[v]]+=hashCG2Area[v]

print("======")
for v in sorted(hashMerge2Area.keys()):
    print("MERGE %d Surface %.2f"%(v, int(hashMerge2Area[v]/100) ))



exit()


def check_validity(geometry):
    return geometry.is_valid

#check = data['geometry'].apply(check_validity)

# Print or manipulate the GeoDataFrame as needed
print("Original GeoDataFrame:")
vals = ( data['geometry'].is_valid.to_numpy() ).astype("int")
print(np.bincount(vals))

areas = data.area.to_numpy()
#for a in areas:
#    print(a)



#vals = [hash_mapping[c] for c in code_cultu ]

#print(np.unique(vals))
#print(len(np.unique(vals)))

#exit()
code_group = code_group.astype("int")
hash_CG2Count = {}

for v in code_group:
    if v not in hash_CG2Count:
        hash_CG2Count[v] =0
    hash_CG2Count[v]+=1

for k in sorted(hash_CG2Count.keys()):
    print("key %d val %d"%(k,hash_CG2Count[k]))


#print(np.bincount(code_group))
exit()

print(code_cultu.shape)


print(np.unique(code_cultu)) 
print(len(np.unique(code_cultu)) )


print(np.unique(code_group.astype("int"))) 
print(len(np.unique(code_group.astype("int"))) )
