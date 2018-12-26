import os

ORIG_IMAGES_PATH = '../images'
THUMB_OUTPUT_PATH = 'out/thumb'
FILE_LIST = 'out/files.txt'

file_names = os.listdir(ORIG_IMAGES_PATH)

thumb_file_paths = [ '{}/{}'.format(THUMB_OUTPUT_PATH, name) for name in file_names ]

def create_file_list():
    if os.path.exists(FILE_LIST):
        os.remove(FILE_LIST)
    
    with open(FILE_LIST, 'w') as file:
        for file_path in thumb_file_paths:
            size = os.path.getsize(file_path)/1024.0
            file.write('{:.1f} {}\n'.format(size, file_path))


def task_file_list():  
    #actions = [ 'echo `ls -sh {} >> {}`'.format(file_path, FILE_LIST) for file_path in thumb_file_paths ]

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
    orig_file_paths = [ '{}/{}'.format(ORIG_IMAGES_PATH, name) for name in file_names ]
    dest_file_paths = [ '{}/{}'.format(THUMB_OUTPUT_PATH, name) for name in file_names ]
    
    orig_to_dest = zip(orig_file_paths, dest_file_paths)
    
    actions = [ 'convert -resize "100x100" {} {}'.format(orig_path, dest_path) for orig_path, dest_path in orig_to_dest ]

    return {
        'file_dep': orig_file_paths,
        'targets': dest_file_paths,
        'actions': actions,
        'clean': True
    }
