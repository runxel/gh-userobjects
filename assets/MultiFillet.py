"""
Provides fillets for curves where the output is one final curve.

    Args:
        crv: The curve to fillet.
        crv_t: Params of 'crv' where it shall fillet.
        radius: The radius (or radii) of the fillets.
    Returns:
        FC: The filleted curve. 
"""

__author__ = "Lucas Becker @runxel"
__version__ = "2019-09-16"

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
from scriptcontext import doc


n_f = 0  # for better help when it fails
n_radius = len(radius)
n_crvparam = len(crv_t)

if (n_radius != n_crvparam) and (n_radius > 1):
    diff_in_size = abs(n_radius - n_crvparam)
    if n_radius < n_crvparam:
        add_error_text = "{} too few radii provided.".format(diff_in_size)
    else:
        add_error_text = "{} too many radii provided.".format(diff_in_size)

    raise RuntimeError("\nMismatch of curve params and radii.\n" + add_error_text)


def shift(l, n):
    return l[n:] + l[:n]

def fillet(crv1, crv2, radius):
    """ Wrapper for Curve.CreateFilletCurves Method """
    global n_f
    # reparam first
    crv1.Domain = rg.Interval(0,1)
    crv2.Domain = rg.Interval(0,1)
    pt1 = crv1.PointAt(0.999)
    pt2 = crv2.PointAt(0.001)

    fillet_crv = rg.Curve.CreateFilletCurves(crv1, pt1, crv2, pt2,
                                             radius, True, True, True,
                                             doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)

    if len(fillet_crv) == 0:
        raise RuntimeError("\nRadius is too big.\nMost possible culprit is [" + str(n_f) + "].")
    n_f += 1

    return fillet_crv[0]  # otherwise we would return an array


# check if input curve is closed
closed = crv.IsClosed
# split the curve at the provided params
splitted = crv.Split(crv_t)
# init the interim result
if closed:
    splitted = shift(splitted, -1)
interim = splitted[0]

for _, i in enumerate(range(len(splitted)-1)):
    # interim will grow until only the last fillet (with itself) remains
    if n_radius > 1:
        interim = fillet(interim, splitted[i+1], radius[i])
    else:
        interim = fillet(interim, splitted[i+1], radius[0])

# final result:
if closed:  # then also do the last fillet with itself
    FC = fillet(interim, interim, radius[-1])
else:       # otherwise we're already done
    FC = interim
