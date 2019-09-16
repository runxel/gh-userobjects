# UserObjects 🦗 for GH 1.0
Grasshopper user objects are files you can add to Grasshopper to enhance and ease your workflow. Mostly they are clustered components. They will reside with the other components, which makes them easy to use.  
Everybody can create them by "File > Create User Object…"  

![multi fillet picture](/assets/img/multi-fillet.png)

---

### [Multi Fillet](UserObjects/Multi%20Fillet.ghuser)
Actually a small [python script](assets/MultiFillet.py) which allows the user to input a curve, curve parameters (= where to fillet) and a radius. This works like the default 'Fillet' component in Grasshopper should work (instead it will generate a new curve for every `t` input…).

### [ShatterInt](UserObjects/ShatterInt.ghuser)
ShatterInt shatters multiple curves at their intersections.

### [Show All Plane Vectors](UserObjects/Show%20All%20Plane%20Vectors.ghuser)
Deconstructs a plane and outputs the basepoint and all the main vectors. Should be used together with the 'Vector Display Ex (VDisEx)' component.

![show all plane vectors picture](/assets/img/showapv.png)
