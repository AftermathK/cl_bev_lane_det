import numpy as np
from scipy.spatial import distance

colors = [
    [203, 213, 104],
    [2, 2, 169],
    [247, 129, 7],
    [236, 184, 69],
    [239, 86, 208],
    [31, 170, 7],
    [24, 166, 169],
    [25, 39, 42],
    [252, 73, 124],
    [52, 31, 161], [156, 24, 38],
    [17, 213, 171],
    [85, 219, 203],
    [75, 195, 52],
    [65, 100, 8],
    [237, 40, 140],
    [169, 83, 76],
    [6, 235, 68],
]

def visualize_2d(image, mask):

    return
def naive_cluster(list, gap, spatial_gap):
    centers = []  # (mean, num)
    cids = []
    for x, y, val in list:
        # if len(centers) == 0:
        #     centers.append((val, 1))
        #     cids.append(len(centers) - 1)
        #     continue
        # find_center = False

        min_gap = gap + 1
        min_cid = -1
        for id, (mean, num) in enumerate(centers):
            diff = abs(val - mean)
            if diff < min_gap:
                min_gap = diff
                min_cid = id
        if min_gap < gap:
            cids.append((x, y, min_cid))
            mean, num = centers[min_cid]
            centers[min_cid] = ((mean * num + val) / (num + 1), num + 1)
        else:
            centers.append((val, 1))
            cids.append((x, y, len(centers) - 1))
    return cids, centers


def naive_cluster_nd(emb_list, gap):
    centers = []  # (mean, num)
    cids = []
    for x, y, emb in emb_list:
        min_gap = gap + 1
        min_cid = -1
        for id, (center, num) in enumerate(centers):
            diff = distance.euclidean(emb, center)
            if diff < min_gap:
                min_gap = diff
                min_cid = id
        if min_gap < gap:
            cids.append((x, y, min_cid))
            center, num = centers[min_cid]
            centers[min_cid] = ((center * num + emb) / (num + 1), num + 1)
        else:
            centers.append((emb, 1))
            cids.append((x, y, len(centers) - 1))
    return cids, centers


def collect_embedding_with_position(seg, emb, conf):
    emb = emb[0]
    assert (len(seg.shape) == 2)
    assert (len(emb.shape) == 2)
    # H, W
    ret = []
    for i in range(seg.shape[0]):
        for j in range(seg.shape[1]):
            if seg[i, j] >= conf:
                ret.append((i, j, emb[i, j]))
    return ret


def collect_nd_embedding_with_position(seg, emb, conf):
    assert (len(seg.shape) == 2)
    assert (len(emb.shape) == 3)
    # H, W
    ret = []
    for i in range(seg.shape[0]):  # H
        for j in range(seg.shape[1]):  # W
            if seg[i, j] >= conf:
                ret.append((i, j, emb[:, i, j]))  # Nd
    return ret


def embedding_post(pred, conf, emb_margin=6.0, min_cluster_size=100, canvas_color=False):
    seg, emb = pred  # [key]
    seg, emb = seg[0][0], emb[0]
    nd, h, w = emb.shape
    # emb_show = (emb - emb.min()).detach().numpy().astype(np.uint8)
    # emb_show[:, seg < 0] = 0
    # cv2.imshow("emb0", emb_show[0] * 5)
    # cv2.imshow("emb1", emb_show[1] * 5)

    # cv2.waitKey(0)

    if nd > 1:
        ret = collect_nd_embedding_with_position(
            seg, emb, conf
        )
        c = naive_cluster_nd(ret, emb_margin)
    elif nd == 1:
        ret = collect_embedding_with_position(
            seg, emb, conf
        )
        c = naive_cluster(ret, emb_margin, None)

    # print(c)
    if canvas_color:
        lanes = np.zeros((*seg.shape, 3), dtype=np.uint8)
    else:
        lanes = np.zeros(seg.shape, dtype=np.uint8)
    # print("Cluster centers:", len(c[1]))
    # print(key, len(list(filter(lambda x: x[1] > 150, c[1]))))
    for x, y, id in c[0]:
        if c[1][id][1] < min_cluster_size:  # Filter small clusters
            continue
        if canvas_color:
            lanes[x][y] = colors[id]
        else:
            lanes[x][y] = id + 1
    return lanes, c[0]
