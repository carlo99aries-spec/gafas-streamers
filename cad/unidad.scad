// ============================================================
//  GAFAS STREAMERS — Módulo B · unidad de cómputo
//  Modelo paramétrico. Cambia un número y vuelve a renderizar.
//  Render:  openscad -o unidad.stl unidad.scad
// ============================================================

/* [Carcasa] */
W     = 78;    // ancho exterior
H     = 64;    // alto exterior
D     = 22;    // grosor exterior
R     = 9;     // radio de esquinas
WALL  = 2;     // pared
LID   = 1.6;   // grosor de tapa

/* [Batería] */
BAT_W = 52;    // ancho del pouch
BAT_H = 56;    // alto del pouch
BAT_D = 10;    // grosor del pouch

/* [Raspberry Pi Zero 2 W] */
PI_HOLE_X = 58;   // separación de agujeros (mm)
PI_HOLE_Y = 23;
PI_POST   = 3.2;  // radio exterior del poste
PI_SCREW  = 1.3;  // radio del agujero (M2.5)

/* [Clip de cinturón] */
CLIP_GAP = 6;
CLIP_W   = 34;
CLIP_H   = 44;
CLIP_T   = 1.6;

/* [Detalle] */
SEG = 72;

part = "ambos";  // [ambos, cuerpo, tapa]

// ------------------------------------------------------------
CAV_H = D - WALL - LID;       // altura interior libre

module rbox(w, h, d, r) {
  hull()
    for (x = [-w/2 + r, w/2 - r])
      for (y = [-h/2 + r, h/2 - r])
        translate([x, y, 0]) cylinder(r = r, h = d, $fn = SEG);
}

module poste() {
  difference() {
    cylinder(r = PI_POST, h = BAT_D + 1, $fn = 28);
    translate([0, 0, BAT_D + 1 - 6])
      cylinder(r = PI_SCREW, h = 7, $fn = 18);
  }
}

module belt_clip() {
  translate([0, 0, -CLIP_GAP])
    rbox(CLIP_W, CLIP_H, CLIP_T, 5);
  translate([-8, CLIP_H/2 - 8, -CLIP_GAP])
    cube([16, 8, CLIP_GAP + 0.1]);
}

module cortes() {
  // USB-C en el borde inferior  (-Y)
  translate([-4.75, -H/2 - 1, D/2 - 1.7])
    cube([9.5, WALL + 2, 3.4]);

  // bandeja SIM en el costado izquierdo  (-X)
  translate([-W/2 - 1, -22, D/2 - 2])
    cube([WALL + 2, 12, 4]);

  // botón en el borde superior  (+Y)
  translate([-7, H/2 - 1, D/2 - 4])
    cube([14, WALL + 2, 8]);

  // LED de estado  (+Y)
  translate([24, H/2 - 1, D/2])
    rotate([-90, 0, 0]) cylinder(r = 1.5, h = WALL + 3, $fn = 24);

  // ranuras de ventilación  (-Y)
  for (i = [-2 : 2])
    translate([i * 9 - 1.2, -H/2 - 1, D/2 - 9])
      cube([2.4, WALL + 2, 18]);

  // línea de unión cuerpo/tapa (parting line)
  translate([0, 0, D - LID - 0.5])
    difference() {
      rbox(W + 2, H + 2, 0.38, R + 1);
      rbox(W - 1.2, H - 1.2, 0.5, R - 0.6);
    }
}

module cuerpo() {
  difference() {
    union() {
      rbox(W, H, D, R);
      belt_clip();
    }
    translate([0, 0, WALL])
      rbox(W - 2*WALL, H - 2*WALL, CAV_H + 0.2, R - WALL);
    cortes();
  }
  for (x = [-PI_HOLE_X/2, PI_HOLE_X/2])
    for (y = [-PI_HOLE_Y/2, PI_HOLE_Y/2])
      translate([x, y, WALL]) poste();
}

module tapa() {
  translate([0, 0, D - LID]) {
    difference() {
      rbox(W, H, LID, R);
    }
    translate([0, 0, -1.3])
      rbox(W - 2*WALL - 0.5, H - 2*WALL - 0.5, 1.4, R - WALL);
  }
}

// ------------------------------------------------------------
if (part == "ambos") { cuerpo(); tapa(); }
if (part == "cuerpo") cuerpo();
if (part == "tapa") tapa();
