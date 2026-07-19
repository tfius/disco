"""Garden-of-Eden / reachability structure for small toroidal Life grids.

Given a functional map f (list where f[s] is the successor of state s), classify
states by reachability and slice the result by population, so questions like
"what is the lightest unreachable state" are one call.

  image_mask(f)                  -> bytearray, 1 iff s has a preimage
  goe_states(f)                  -> sorted list of unreachable states
  pop_histogram(f)               -> (goe_hist, reach_hist) dicts pop -> count
  extremes(f)                    -> (min_goe_pop, n_at_min, max_reach_pop, n_at_max)
  preimages(f)                   -> dict s -> list of preimages (only non-empty)
  preimage_of(f, target)         -> list of preimages of one state
  render(s, W, H)                -> multiline '#'/'.' picture
  displacement(s, W, H)          -> canonical (dr,dc) for a population-2 state
  class_counts(f, W, H, pop=2)   -> (goe_classes, reach_classes) keyed by displacement
"""


def image_mask(f):
    m = bytearray(len(f))
    for s in range(len(f)):
        m[f[s]] = 1
    return m


def goe_states(f):
    m = image_mask(f)
    return [s for s in range(len(f)) if not m[s]]


def pop_histogram(f):
    m = image_mask(f)
    goe, reach = {}, {}
    for s in range(len(f)):
        p = bin(s).count('1')
        d = reach if m[s] else goe
        d[p] = d.get(p, 0) + 1
    return goe, reach


def extremes(f):
    goe, reach = pop_histogram(f)
    if goe:
        mn = min(goe)
        mn_c = goe[mn]
    else:
        mn, mn_c = None, 0
    if reach:
        mx = max(reach)
        mx_c = reach[mx]
    else:
        mx, mx_c = None, 0
    return mn, mn_c, mx, mx_c


def preimages(f):
    pre = {}
    for s in range(len(f)):
        pre.setdefault(f[s], []).append(s)
    return pre


def preimage_of(f, target):
    return [s for s in range(len(f)) if f[s] == target]


def render(s, W, H):
    return '\n'.join(
        ''.join('#' if (s >> (r * W + c)) & 1 else '.' for c in range(W))
        for r in range(H))


def displacement(s, W, H):
    b = [i for i in range(W * H) if (s >> i) & 1]
    if len(b) != 2:
        raise ValueError("displacement() needs a population-2 state")
    (r0, c0) = (b[0] // W, b[0] % W)
    (r1, c1) = (b[1] // W, b[1] % W)
    d = ((r1 - r0) % H, (c1 - c0) % W)
    return min(d, ((-d[0]) % H, (-d[1]) % W))


def class_counts(f, W, H, pop=2):
    if pop != 2:
        raise ValueError("class_counts currently only classifies population-2 states")
    m = image_mask(f)
    goe, reach = {}, {}
    for s in range(len(f)):
        if bin(s).count('1') != 2:
            continue
        d = displacement(s, W, H)
        t = reach if m[s] else goe
        t[d] = t.get(d, 0) + 1
    return goe, reach
