import os
import glob

from fprules import file_pattern 

IMAGES_SRC_GLOB = '../images/*.png'
THUMB_DEST_GLOB = 'out/thumb/*.png'
IMAGES_SRC_PATH = '../images'
THUMB_DEST_PATH = 'out/thumb'
FILE_LIST = 'out/files.txt'

orig_file_paths = glob.glob(IMAGES_SRC_GLOB)
thumb_file_paths = [ os.path.normpath(path.replace(IMAGES_SRC_PATH, THUMB_DEST_PATH)) for path in orig_file_paths ]

def create_file_list(dependencies):
    if os.path.exists(FILE_LIST):
        os.remove(FILE_LIST)
    
    with open(FILE_LIST, 'w') as file:
        for file_path in dependencies:
            size = os.path.getsize(file_path)/1024.0
            file.write('{:.1f} {}\n'.format(size, file_path))


def task_file_list():
    return {
        'file_dep': thumb_file_paths,
        'targets': [FILE_LIST],
        'actions': [create_file_list],
        'clean': True
    }


def task_convert():
    if not os.path.exists('out'):
        os.mkdir('out')
    if not os.path.exists('out/thumb'):
        os.mkdir('out/thumb')

    for data in file_pattern(IMAGES_SRC_GLOB, THUMB_DEST_GLOB.replace('*', '%')):
        yield {
            'name': data.name,
            'file_dep': [data.src_path],
            'actions': ['magick {} -resize "100x100" {}'.format(data.src_path, data.dst_path)],
            'targets': [data.dst_path],
            'clean': True
        }
