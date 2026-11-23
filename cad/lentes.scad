// ============================================================
//  GAFAS STREAMERS — Módulo A · lentes
//  Modelo paramétrico. Estilo Ray-Ban Meta.
//  Render:  openscad -o lentes.stl lentes.scad
// ============================================================

/* [Optica] */
LENS_W  = 52;     // ancho del cristal
LENS_H  = 40;     // alto del cristal
RIM     = 3;      // grosor del aro
DEPTH   = 4.5;    // profundidad del frente
LENS_R  = 18;     // radio de esquina del cristal
SEP     = 40;     // separacion de centros al eje
BRIDGE  = 20;     // luz del puente

/* [Patillas] */
TEMPLE_L = 142;
TEMPLE_W = 5.0;
TEMPLE_H = 9.5;
TEMPLE_WALL = 1.4;

/* [Detalle] */
CAM_R   = 4.2;
CAM_X   = -58;
CAM_Y   = 17;
SEG     = 64;

part = "ambos";  // [ambos, frente, patillas]

// ------------------------------------------------------------
module rrect(w, h, r) {
  hull()
    for (x = [-w/2 + r, w/2 - r])
      for (y = [-h/2 + r, h/2 - r])
        translate([x, y]) circle(r = r, $fn = SEG);
}

module aro(cx) {
  translate([cx, 0, 0])
    difference() {
      linear_extrude(DEPTH, center = true)
        rrect(LENS_W + 2*RIM, LENS_H + 2*RIM, LENS_R + RIM);
      // apertura del cristal
      linear_extrude(DEPTH + 2, center = true)
        rrect(LENS_W, LENS_H, LENS_R);
      // rebaje frontal para asentar el cristal
      translate([0, 0, DEPTH/2 - 0.6])
        linear_extrude(1.2)
          rrect(LENS_W + 1.4, LENS_H + 1.4, LENS_R + 0.7);
    }
}

module puente() {
  hull() {
    translate([-SEP + LENS_W/2 + RIM - 2, 10, 0])
      cube([6, 7, DEPTH], center = true);
    translate([ SEP - LENS_W/2 - RIM + 2, 10, 0])
      cube([6, 7, DEPTH], center = true);
  }
}

module bisagra(side) {
  translate([side * (SEP + LENS_W/2 + RIM), 3, 0])
    cube([5, 11, DEPTH + 1], center = true);
}

module patilla_volumen(side, t) {
  hull() {
    translate([side * (SEP + LENS_W/2 + RIM), 3, 0])
      cube([TEMPLE_W * t, TEMPLE_H * t, 3], center = true);
    translate([side * 56, -6, -TEMPLE_L])
      cube([TEMPLE_W * t, TEMPLE_H * t, 3], center = true);
  }
}

module patilla(side) {
  difference() {
    patilla_volumen(side, 1.0);
    patilla_volumen(side, 0.66);
    // abrir el extremo trasero (entrada del cable / contactos)
    translate([side * 56, -6, -TEMPLE_L - 1])
      cube([12, 14, 6], center = true);
    // ranura de alivio para los dedos del gancho
    translate([side * 40, -6, -TEMPLE_L + 16])
      cube([10, 3.2, 22], center = true);
  }
}

module camara() {
  translate([CAM_X, CAM_Y, DEPTH/2 - 1.2])
    cylinder(r = CAM_R, h = 4, $fn = 32, center = true);
  translate([CAM_X, CAM_Y, DEPTH/2 - 0.4])
    cylinder(r = 2.2, h = 3, $fn = 24, center = true);
}

module micros() {
  for (p = [[-46, -14], [46, -14], [0, 20]])
    translate([p[0], p[1], DEPTH/2])
      cylinder(r = 0.9, h = 4, $fn = 16, center = true);
}

module parlante() {
  // rejilla en la patilla derecha, junto al oido
  for (i = [0:5]) {
    translate([62, -1 + i * 1.6, -104])
      rotate([90, 0, 0])
        cylinder(r = 0.7, h = 4, $fn = 12, center = true);
  }
}

module contactos() {
  for (i = [-1, 1]) {
    translate([-56 + i * 2.6, -9, -TEMPLE_L + 4])
      rotate([90, 0, 0])
        cylinder(r = 1.1, h = 5, $fn = 16, center = true);
  }
}

module frente() {
  difference() {
    union() {
      aro(-SEP);
      aro( SEP);
      puente();
      bisagra(-1);
      bisagra(1);
    }
    camara();
    micros();
  }
}

// ------------------------------------------------------------
if (part == "ambos") { frente(); patilla(-1); patilla(1); parlante(); contactos(); }
if (part == "frente") frente();
if (part == "patillas") { patilla(-1); patilla(1); parlante(); contactos(); }
