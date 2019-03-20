import numpy as np


def img2count(img, exposure):
    count = np.sum(
        np.sum(img)) / 1e9 / (10 * (2 ** exposure)
    )

    return count


def crop_imgs(imgs):
    bounds = (
        ((0, 350), (175, 525)),
        ((55, 405), (200, 550)),
        ((0, 350), (140, 490))
    )
    new_imgs = []

    for i, img in enumerate(imgs):
        b = bounds[i]
        new_imgs.append(img[b[0][0]:b[0][1],b[1][0]:b[1][1]])

    return new_imgs