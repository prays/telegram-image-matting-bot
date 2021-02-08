import os
import sys
import argparse
import numpy as np
import cv2
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms

from src.models.modnet import MODNet


if __name__ == '__main__':
    # define cmd arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-path', type=str, help='path of input images')
    parser.add_argument('--output-path', type=str, help='path of output images')
    parser.add_argument('--file-output', type=str, help='filename of output images')
    parser.add_argument('--ckpt-path', type=str, help='path of pre-trained MODNet')
    args = parser.parse_args()

    # check input arguments
    if not os.path.exists(args.input_path):
        print('Cannot find input path: {0}'.format(args.input_path))
        exit()
    if not os.path.exists(args.output_path):
        print('Cannot find output path: {0}'.format(args.output_path))
        exit()
    if not os.path.exists(args.ckpt_path):
        print('Cannot find ckpt path: {0}'.format(args.ckpt_path))
        exit()

    torch_transforms = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ]
    )

    #GPU = True if torch.cuda.device_count() > 0 else False

    # define hyper-parameters
    ref_size = 512

    # define image to tensor transform
    im_transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ]
    )

    # create MODNet and load the pre-trained ckpt
    modnet = MODNet(backbone_pretrained=False)
    modnet = nn.DataParallel(modnet)#.cuda()
    modnet.load_state_dict(torch.load(args.ckpt_path, map_location=torch.device('cpu')))
    modnet.eval()

    # inference images

    frame_np = cv2.imread('{}'.format(args.input_path))
    #print(frame_np.shape)
    (width, height, channel) = frame_np.shape
    #print(frame_np)
    frame_np = cv2.cvtColor(frame_np, cv2.COLOR_BGR2RGB)
    frame_np = cv2.resize(frame_np, (910, 512), cv2.INTER_AREA)
    frame_np = frame_np[:, 120:792, :]
    frame_np = cv2.flip(frame_np, 1)

    frame_PIL = Image.fromarray(frame_np)
    frame_tensor = torch_transforms(frame_PIL)
    frame_tensor = frame_tensor[None, :, :, :]
    #if GPU:
    #    frame_tensor = frame_tensor.cuda()
    
    with torch.no_grad():
        _, _, matte_tensor = modnet(frame_tensor, True)

    matte_tensor = matte_tensor.repeat(1, 3, 1, 1)
    matte_np = matte_tensor[0].data.cpu().numpy().transpose(1, 2, 0)
    fg_np = matte_np * frame_np + (1 - matte_np) * np.full(frame_np.shape, 255.0)
    #view_np = np.uint8(np.concatenate((frame_np, fg_np), axis=1))
    #view_np = cv2.cvtColor(view_np, cv2.COLOR_RGB2BGR)
    view_np = cv2.cvtColor(np.uint8(fg_np), cv2.COLOR_RGB2BGR)
    view_np = cv2.resize(view_np, (height, width))

    #matte_name = 'img_out.png'
    cv2.imwrite('{}'.format(os.path.join(args.output_path, args.file_output)), view_np)
