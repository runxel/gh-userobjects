"""
Provides fillets where the output is one final curve.

    Args:
        crv: The curve to fillet. {curve}
        crv_t: Params of 'crv' where it shall fillet. {float | List access}
        radius: The radius of the fillet. {float}
    Returns:
        fcrv: The filleted curve. 
"""

__author__ = "Lucas Becker @runxel"
__version__ = "2019-07-08"

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
from scriptcontext import doc

if not radius:
    radius = doc.ModelAbsoluteTolerance * 10

def fillet(crv1, crv2, radius):
    """ Wrapper for Curve.CreateFilletCurves Method """
    # reparam first
    crv1.Domain = rg.Interval(0,1)
    crv2.Domain = rg.Interval(0,1)
    pt1 = crv1.PointAt(0.9)
    pt2 = crv2.PointAt(0.1)

    fillet_crv = rg.Curve.CreateFilletCurves(crv1, pt1, crv2, pt2,
                                             radius, True, True, True,
                                             doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
    return fillet_crv[0]  # otherwise we would return an array


# check if input curve is closed
closed = crv.IsClosed
# split the curve at the provided params
splitted = crv.Split(crv_t)
# init the interim result
interim = splitted[0]

for _, i in enumerate(range(len(splitted)-1)):
    # interim will grow until only the last fillet (with itself) remains
    interim = fillet(interim, splitted[i+1], radius)

# final result:
if closed:  # then also do the last fillet with itself
    fcrv = fillet(interim, interim, radius)
else:       # otherwise we're already done
    fcrv = interim
