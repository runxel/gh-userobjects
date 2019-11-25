"""
Provides filleting and chamfering for curves where the output is one final curve.
-
Version: 191125

    Args:
        crv:    The curve to operate on. {curve}
        crv_t:  Params of 'crv' where it shall fillet/chamfer. {float | List access (!)}
        radius: The radius of the fillet or the distance of the chamfer. {float}
    Returns:
        crv_out: The filleted or chamfered curve. 
"""

__author__ = "Lucas Becker @runxel"
__version__ = "2019-11-25"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
from scriptcontext import doc

e = Grasshopper.Kernel.GH_RuntimeMessageLevel.Error
w = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning

class Mfc(component):
    def __init__(self):
        super(Mfc, self).__init__()
        self.chamfer_enabled = False

        self.exc_msg = "Something's gone wrong. Sorry 'bout that."

    def RunScript(self, crv, crv_t, radius):

        if not crv:
            self.AddRuntimeMessage(w, "Component is missing an input curve.")
            return  # stop this

        if not crv_t:
            self.AddRuntimeMessage(w, "Component is missing a parameter.")
            return  # stop this

        if not radius:
            self.AddRuntimeMessage(w, "Component is missing a radius")
            return  # stop this

        self.fillet = lambda c1, c2, r : fillet(c1, c2, r)
        self.chamfer = lambda c1, c2, r : chamfer(c1, c2, r)
        try: # pretty brutal method, but seems to work
            self.call
        except:
            self.call = self.fillet

        # check if input curve is closed
        self.closed = crv.IsClosed
        if self.closed:
            self.final_point = crv.PointAt(crv_t[0])
        # split the curve at the provided params
        splitted = crv.Split(crv_t)
        # init the interim result
        interim = splitted[0]

        # note how we reduce the length by one bc input crv might be closed
        for _, i in enumerate(range(len(splitted)-1)):
            # interim will grow until only the last fillet 
            # (with itself) remains – if closed
            interim = self.call(interim, splitted[i+1], radius)

        # final result:
        if self.closed:
            # we need the new param of what was originally the last point where to f/c
            last_point_param = rg.Curve.ClosestPoint(interim, self.final_point, 0)[1]
            if self.chamfer_enabled:
                # split again at last point
                last_split = interim.Split(last_point_param)
                crv_out = chamfer(last_split[0], last_split[1], radius)
            else:
                # change the seam back to original place so we can fillet there
                _seamChangeSuccess = interim.ChangeClosedCurveSeam(last_point_param)
                # we call fillet() with the optional parameters of where to have the point
                crv_out = fillet(interim, interim, radius, 1,0)
        else:       # otherwise we're already done
            crv_out = interim

        return crv_out


    def OnTextMenuClick(self, sender, args):
        try: #always use try
            self.chamfer_enabled = not self.chamfer_enabled
            self.call = self.chamfer if self.chamfer_enabled else self.fillet
            
            self.ExpireSolution(True)

        except Exception, ex:
            out = self.exc_msg


    def AppendAdditionalMenuItems(self, items):
        component.AppendAdditionalMenuItems(self, items)

        try:
            image = None
            item = items.Items.Add("Chamfer", image, self.OnTextMenuClick)
            item.Checked = self.chamfer_enabled
        except Exception, ex:
            out = self.exc_msg


def fillet(crv1, crv2, radius, pt1at=0.9, pt2at=0.1):
    """ Wrapper for Curve.CreateFilletCurves Method """
    # reparam first
    crv1.Domain = rg.Interval(0,1)
    crv2.Domain = rg.Interval(0,1)
    # if you would use CurveEnd method both points
    # then are at the same spot; they ought to be discrete
    pt1 = crv1.PointAt(pt1at)
    pt2 = crv2.PointAt(pt2at)
    """ Interestingly we need to specify the PointAt param differently 
        for the last fillet (when closed).
        Normally it needs to be 0.9 and 0.1 so the points are discrete, otherwise
        the method will fail.
        However, if we do the last fillet, then there is no other curve left, so
        we fillet the curve with itself. In this case the param have to be 1 and 0.
        Why? I have no fucking clue.
        Wasted time here: about 5 hours.
    """

    fillet_crv = rg.Curve.CreateFilletCurves(crv1, pt1, crv2, pt2,
                                             radius, True, True, True,
                                             doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
    try:
        fillet_crv[0]
    except:
        raise ValueError(" Radius might be to big.")
    return fillet_crv[0]  # otherwise we would return an array


def chamfer(crv1, crv2, radius):
    """ RhinoCommon has no dedicated Chamfer method,
        so you start to write your own.
    """
    curve_start = rg.CurveEnd.Start
    curve_end = rg.CurveEnd.End
    
        
    cc1 = rg.Curve.Trim(crv1, curve_end, radius)
    cc2 = rg.Curve.Trim(crv2, curve_start, radius)
    
    if (cc1 is None) or (cc2 is None):
        raise ValueError(" Radius might be to big.")

    cc1p = cc1.PointAtEnd
    cc2p = cc2.PointAtStart

    new_line = rg.LineCurve(cc1p, cc2p)

    coll = [cc1, new_line, cc2]

    chamfer_crv = rg.Curve.JoinCurves(coll, doc.ModelAbsoluteTolerance, True)

    return chamfer_crv[0]  # otherwise we would return an array
