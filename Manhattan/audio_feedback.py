from playsound3 import *
import random, os
# error_path = 'D:/Excel Datasets/Manhattan/Audio/Error'
# success_path = 'D:/Excel Datasets/Manhattan/Audio/Success'

# def error(error_path):
#     files = []
#     for i in os.listdir(error_path):
#         files.append('/'.join([error_path, i]))
#     return playsound(random.choice(files))
#
# def success(success_path):
#     files = []
#     for i in os.listdir(success_path):
#         files.append('/'.join([success_path, i]))
#     return playsound(random.choice(files))

def feedback_sound(action):
    try:
        path = '/'.join(['D:/Excel Datasets/Manhattan/Audio', 'Error/' if action == 'Error' else 'Success/'])
        # if action == 'Error':
        #     path = '/'.join([path, action])
        # elif action == 'Success':
        #     path = 'D:/Excel Datasets/Manhattan/Audio/Success'
        # else:
        #     pass
        # print(''.join([path, random.choice(os.listdir(path))]))
        return playsound(''.join([path, random.choice(os.listdir(path))]))
    except:
        pass

path = 'D:/Excel Datasets/Manhattan/Audio'
action = 'Success'
print('/'.join([path, 'Error/' if action == 'Error' else 'Success/']))
feedback_sound('Error')