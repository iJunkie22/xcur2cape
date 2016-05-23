import math


FL = 24


sample = range(0, 1000)

for i in sample:
    frame_list = sample[:i]
    o = i - FL
    if o > 0:
        k = math.ceil((float((o % FL) + i) / float(FL)))
        r = len(frame_list[0::int(k)])
    else:
        k = 1
        r = len(frame_list)
    print "{:>10}  {:>10}  {:>10}  {:>10}  [{:<24}]  ".format(i, o, k, r, "|" * r) \
          + str("!!!!!!!!!!!!!!" * int(bool(r > FL)))


