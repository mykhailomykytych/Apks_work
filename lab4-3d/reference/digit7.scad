// Reference model for lab 4 (group KI-407 -> digit "7").
// Used only to check dimensions and printability; the lab itself is done
// in AutoCAD and Fusion 360 with the same dimensions.
T      = 8;     // digit thickness, mm
EMB    = 1.5;   // surname: convex (boss) height
DEB    = 2.0;   // name: concave (cut) depth
FONT   = "DejaVu Sans:style=Bold";

// 2D outline of the digit 7 (mm)
module seven() {
    polygon([[0,100],[70,100],[70,82],[38,0],[14,0],[46,78],[0,78]]);
}
// diagonal stroke: centre line from (26,0) to (58,80)
ANG  = atan2(80, 32);           // ~68.2 deg
module on_diag(t, off) {        // t: distance along the stroke, off: perpendicular shift
    translate([26 + t*cos(ANG) - off*sin(ANG), t*sin(ANG) + off*cos(ANG), 0]) rotate(ANG) children();
}

difference() {
    union() {
        linear_extrude(T) seven();
        // Surname - convex, on the top bar
        translate([35, 89, T]) linear_extrude(EMB)
            text("МИКИТИЧ", size=7, font=FONT, halign="center", valign="center");
    }
    // Name - concave, along the diagonal stroke
    translate([0,0,T-DEB]) linear_extrude(DEB+1)
        on_diag(42, 4.2) text("МИХАЙЛО", size=5.5, font=FONT, halign="center", valign="center");
    // Patronymic - through cut, along the diagonal stroke
    translate([0,0,-1]) linear_extrude(T+2)
        on_diag(42, -4.2) text("ВАСИЛЬОВИЧ", size=5, font=FONT, halign="center", valign="center");
}
