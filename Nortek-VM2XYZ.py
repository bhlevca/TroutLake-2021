import os
import csv
import math
import numpy as np
from numpy import linalg as la
from datetime import datetime
import matplotlib.dates as dates
from matplotlib.dates import date2num
import configparser
from scipy.interpolate import interp1d
#local imports
import utils.Timer as Timer


def read_Nortek_VM_file(filename, delimiter, interval=None):
    """
    Read data from the processed from binary ADCP text file
    :param mname:
    :param delimiter:
    :param interval:
    :return:
    """

    if interval is not None:
        start_num = interval[0]
        end_num = interval[1]
    else:
        start_num = None
        end_num = None
    try:
        with Timer.Timer() as t:

            ifile = open(filename, "rt")
            reader = csv.reader(ifile, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)

            num_recs = 0
            for row in reader:
                num_recs += 1
            ifile.close()
            # reset the iterator reader.seek(0) works only with bytes
            ifile = open(filename, "rt")
            reader = csv.reader(ifile, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)

            long = []  # np.zeros((num_recs-2), dtype=np.ndarray)
            lat = []  # np.zeros((num_recs - 2), dtype=np.ndarray)
            depth = []  # np.zeros((num_recs - 2), dtype=np.ndarray)
            veast = []  # np.zeros((num_recs - 2), dtype=np.ndarray)
            vnorth = []  # np.zeros((num_recs - 2), dtype=np.ndarray)
            vel_avg = []  # np.zeros((num_recs - 2), dtype=np.ndarray)
            dir_avg = []  # np.zeros((num_recs - 2), dtype=np.ndarray)
            str_date_arr = []  # np.zeros((num_recs - 2), dtype=np.str)
            num_date_arr = []  # np.zeros((num_recs - 2), dtype=np.float)

            rowno = 0
    
            for row in reader:
                if rowno == 0:
                    header = row
                    rowno += 1
                    continue
                
                colno = 0
                for col in row:
                    if colno == 0:
                        date_str = col
                        format = "%Y-%m-%dT%H:%M:%S.%f".rstrip('0')
                        dt = datetime.strptime(date_str, format)
                        date_num = date2num(dt)
                        if interval is not None:
                            if start_num > date_num or end_num < date_num:
                                # this row does not qualify
                                skip = True
                                break
                        str_date_arr.append(date_str)
                        num_date_arr.append(date_num)
                    else:
                        if "BeamDepth" in header[colno]:
                            depth.append('-' + col)
                        if "LAT" in header[colno]:
                            lat.append(col)
                        if "LON" in header[colno]:
                            long.append(col)
                        if "VEast" in header[colno]:
                            veast.append(col)
                        if "VNorth" in header[colno]:
                            vnorth.append(col)
                        if "Vel_avg" in header[colno]:
                            vel_avg.append(col)
                        if "Dir_Avg" in header[colno]:
                            dir_avg.append(col)
                    colno += 1

                rowno += 1

            ifile.close()
    finally:
        print('Read took %.03f sec.' % t.interval)

    return [np.array(str_date_arr), np.array(num_date_arr), 
            np.array(long), np.array(lat), np.array(depth),
            np.array(veast), np.array(vnorth), 
            np.array(vel_avg), np.array(dir_avg)
            ]
            
def create_xyz(filename, latarr, longarr, deptharr):
    ifile = open(filename, "wt")
    writer = csv.writer(ifile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
    for lat, long, depth in zip(latarr, longarr, deptharr):
        writer.writerow([long, lat, depth])
    ifile.close()
            
if __name__ == '__main__':
    filename1 = "/software/SAGEwork/Trout_Lake-2021/102478_20210616T172940UTC.CSV"
    filename2 = "/software/SAGEwork/Trout_Lake-2021/102478_20210616T182922UTC.CSV"
    filename3 = "/software/SAGEwork/Trout_Lake-2021/102478_20210616T192922UTC.CSV"
    set1 = read_Nortek_VM_file(filename1, ',')
    [str_date_arr1, num_date_arr1, long1, lat1, depth1, veast1, vnorth1, vel_avg1, dir_avg1] = set1
    set2 = read_Nortek_VM_file(filename2, ',')
    [str_date_arr2, num_date_arr2,long2, lat2, depth2, veast2, vnorth2, vel_avg2, dir_avg2] = set2
    set3 = read_Nortek_VM_file(filename3, ',')
    [str_date_arr3, num_date_arr3,long3, lat3, depth3, veast3, vnorth3, vel_avg3, dir_avg3] = set3
    
    lat = np.concatenate([lat1, lat2, lat3])
    long= np.concatenate([long1, long2, long3])
    depth= np.concatenate([depth1, depth2, depth3])
    
    outfilename = "/software/SAGEwork/Trout_Lake-2021/TroutLake_Nortek_Bathy.xyz"
    create_xyz(outfilename, lat, long, depth)