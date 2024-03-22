import os
from datetime import datetime
import shutil

def file_deleter():
    dir_name = 'deletion'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f'Directory \'{dir_name}\' created.')
    today_date = datetime.now().date().isoformat()
    file_name = os.path.join(dir_name, f'{today_date}.txt')
    open(file_name, 'w').close()
    other_files = [f for f in os.listdir(dir_name) if f != f'{today_date}.txt']
    if other_files:
        print('Yes')
        for file in other_files:
            file_path = os.path.join(dir_name, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f'File \'{file}\' deleted.')

        folders_to_delete = ['zips', 'certificates']
        for folder in folders_to_delete:
            try:
                shutil.rmtree(folder)
                print(f'Deleted folder: {folder}')
            except FileNotFoundError:
                print(f'Folder not found: {folder}')
            except Exception as e:
                print(f'Error deleting folder {folder}: {e}')
    else:
        print('Hi DAD!')
