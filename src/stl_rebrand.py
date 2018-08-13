import csv
import os
import shutil
from time import gmtime, strftime
from itertools import zip_longest

"""
strange loop
Package
GUI
Error logging (try/except
"""

stl_master_location = 'B:\\Share04\\OSTENG02\\'                                          # The parent folder of where the stls are kept   'B:\\Share04\\OSTENG02\\'
mam_stl_import_watchfolder = 'B:\\Share15\\ADsuite\\AD Output\\send_subtitle_file_to_mam\\'      # Where renamed .stls are delivered to for MAM import B:\\Share15\\ADsuite\\AD Output\\send_subtitle_file_to_mam\\


rename_stl_instructions = "D:\\python\\WPy-3661\\code\\csv_watch\\laworder_to_enfield.csv"                  # Where to watch for csv
full_holding_path = 'D:\\python\\WPy-3661\\code\\holding'                           # Where the .stls are copied to from ARCH folder
full_holding_path_with_slash = full_holding_path + '\\'                             # Where the .stls are copied to from ARCH folder
full_holding_path_eng = full_holding_path_with_slash + 'eng\\'                      # Where the .eng.stls are copied to from ARCH folder
log_file_location = 'D:\\python\\WPy-3661\\code\\log\\'                             # Where the output of this script is logged
delete_folder = 'D:\\python\\WPy-3661\\code\\holding\\eng\\delete\\'                # Transiant storage for duplicate files


def create_directory_list_of_stls(dir):
    file_list = []
    for entry in os.scandir(dir):
        if entry.name.lower().endswith('.stl'):
            file_list.append(entry.name)

    return file_list

def create_dict_from_csv():
    dict_list = []
    with open (rename_stl_instructions, 'r') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        for row in reader:
            dict_list.append(row)
            row['source_dir'] = ''
            row['des_dir'] = ''
            row['file_to_copy'] = ''
            row['copy_status'] = ''
        return dict_list

def find_location_of_src_and_dest(dict):
    for source in dict:
        source_dir = 'ARCH'+source['source'][:3]
        dest_dir = 'ARCH'+source['dest'][:3]
        source['source_dir'] = stl_master_location + source_dir
        source['des_dir'] = stl_master_location + dest_dir
    return dict

def create_list_of_source_directories(dict):
    source_folders = []
    updated_dict = {}
    for item in dict:
        source_folders.append(item['source_dir'])
    unique_sources = set(source_folders)
    source_folders_to_scan = list(unique_sources)
    for i in source_folders_to_scan:
        updated_dict[i] = '[]'
    return (updated_dict)

    return source_folders_to_scan

def create_list_of_files(dict):
    ext_tuple = ['stl', 'STL']
    file_list = []
    for key in dict:
        for entry in os.scandir(key):
            if len(entry.name) == 12 and entry.name.endswith(tuple(ext_tuple)):
                file_list.append(key + '\\' + entry.name)
            elif len(entry.name) == 16 and entry.name.endswith(tuple(ext_tuple)):
                file_list.append(key + '\\' + entry.name)
    return file_list

def find_files_to_copy(list_of_file, dict):
    for id, file in [(id, file) for id in dict for file in list_of_file]:
        if id['source'] in file:
            id['file_to_copy'] = file
            id['copy_status'] = 'source stl found'
    for item in dict:
        if item['copy_status'] != 'source stl found':
            item['copy_status'] = 'source stl missing'
    return dict

def copy_stl_to_holding(dict):
    missing_list = []
    for item in dict:
        if item['copy_status'] == 'source stl found':
            if 'eng.stl' in item['file_to_copy'].lower():
                shutil.copy2(item['file_to_copy'], full_holding_path_eng)
                # log(file + ' copied from source file to eng holding area', output_to_console=True)
            elif 'stl' in item['file_to_copy'].lower():
                shutil.copy2(item['file_to_copy'], full_holding_path)
                # log(file + ' copied from source file to holding area', output_to_console=True)
        elif item['copy_status'] == 'source stl missing':
            missing_list.append(item['source'])
    return missing_list

def rename_eng_folder():
    eng_list = create_directory_list_of_stls(full_holding_path_eng)
    for file in eng_list:
        try:
            os.rename(full_holding_path_eng + file, full_holding_path_eng + file[:8] + '.stl')
        except:
            os.replace(full_holding_path_eng + file, delete_folder + file) #Moves stl to delete folder if it already exists in eng folder
            pass

def merge_eng_to_holding():
    list_of_files = create_directory_list_of_stls(full_holding_path_eng)
    for file in list_of_files:
        try:
            os.rename(full_holding_path_eng + file, full_holding_path_with_slash + file)
        except:
            os.replace(full_holding_path_eng + file, delete_folder + file)
            pass

def update_file_name_to_eng(dict):
    list_of_eng_files = create_directory_list_of_stls(full_holding_path_with_slash)
    for item in dict:
        for file in list_of_eng_files:
            if file.startswith(item['source']):
                os.replace(full_holding_path_with_slash + file, full_holding_path_with_slash + item['dest'] + '.eng.stl')
                # log(item['source'] + ' renamed to ' + item['dest'] + ' in holding area', output_to_console=True)
    renamed_list = create_directory_list_of_stls(full_holding_path_with_slash)
    return renamed_list

def copy_to_mam_folder(list):
    copied_to_mam_list = []
    for file in list:
        if os.path.exists(mam_stl_import_watchfolder + file) == False:
            shutil.copy2(full_holding_path_with_slash + file, mam_stl_import_watchfolder + file)
            copied_to_mam_list.append(file)

    return copied_to_mam_list

def copy_to_arch_folder():
    list_of_files = create_directory_list_of_stls(full_holding_path_with_slash)
    copied_to_arch_list = []
    already_in_arch_list = []
    for file in list_of_files:
        destination_file_name = stl_master_location + 'ARCH' + file[:3] + '\\' + file
        if os.path.isfile(destination_file_name) == False:
                shutil.copy2(full_holding_path_with_slash + file, destination_file_name)
                copied_to_arch_list.append(file)
        else:
            shutil.move(full_holding_path_with_slash + file, delete_folder + file)
            already_in_arch_list.append(file)
    return copied_to_arch_list, already_in_arch_list

def move_to_delete():
    move_list = create_directory_list_of_stls(full_holding_path_with_slash)
    for item in move_list:
        os.rename(full_holding_path_with_slash + item, delete_folder + item)


def clear_deleted_items():
    delete_list = create_directory_list_of_stls(delete_folder)
    deleted_list = []
    for item in delete_list:
        os.remove(delete_folder + item)
        deleted_list.append(item)

def WriteListToCSV(missing_list, mam_list, arch_list, already_in_arch_list):
    csv_columns = ['No Source stl file', 'Delivered to MAM', 'Delivered to Archive', 'Already a copy in Archive']
    rows = zip_longest(missing_list, mam_list, arch_list, already_in_arch_list)
    current_time = strftime("%d %b %Y %H %M %S", gmtime())
    csv_log_fn = 'STL Rebrand Log - {}.csv'.format(current_time)
    with open(log_file_location + csv_log_fn, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(csv_columns)
            for data in rows:
                writer.writerow(data)
            writer.writerow('')
            writer.writerow(['csv_source: ', rename_stl_instructions])
            csvfile.close()

def main_programme():
    dictionary = create_dict_from_csv()
    updated_dictionary = find_location_of_src_and_dest(dictionary)
    source_folders_to_scan = create_list_of_source_directories(updated_dictionary)
    list_of_files = create_list_of_files(source_folders_to_scan)
    dict_with_locations= find_files_to_copy(list_of_files, updated_dictionary)
    missing_list = copy_stl_to_holding(dict_with_locations)
    rename_eng_folder()
    merge_eng_to_holding()
    eng_list = update_file_name_to_eng(dict_with_locations)
    mam_list = copy_to_mam_folder(eng_list)
    arch_list, already_arch = copy_to_arch_folder()
    move_to_delete()
    clear_deleted_items()
    WriteListToCSV(missing_list, mam_list, arch_list, already_arch)

main_programme()



