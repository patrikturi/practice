import os
import glob

IMAGES_SRC_GLOB = '../images/*.png'
IMAGES_SRC_PATH = '../images'
THUMB_DEST_PATH = 'out/thumb'
FILE_LIST = 'out/files.txt'

orig_file_paths = glob.glob(IMAGES_SRC_GLOB)
thumb_file_paths = [ path.replace(IMAGES_SRC_PATH, THUMB_DEST_PATH) for path in orig_file_paths ]

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

    orig_to_dest = zip(orig_file_paths, thumb_file_paths)
    actions = [ 'convert -resize "100x100" {} {}'.format(orig_path, dest_path) for orig_path, dest_path in orig_to_dest ]

    return {
        'file_dep': orig_file_paths,
        'targets': thumb_file_paths,
        'actions': actions,
        'clean': True
    }
