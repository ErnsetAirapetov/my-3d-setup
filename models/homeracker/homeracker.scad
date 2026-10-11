// homeracker.scad — переиспользуемые примитивы для адаптации моделей под HomeRacker.
//
// Размеры сняты с официальной пластины «HomeRacker RaspberryPi mount» (Wargazmo):
// шаг сетки 15 мм, ушко 2 мм, квадратное отверстие под lockpin 4.25 мм,
// зазор 0.25 мм с каждой стороны модуля (2u = 29.5 мм, 8u = 119.5 мм).
//
// Подключение: use <homeracker.scad>

HR_UNIT  = 15;    // шаг сетки, мм
HR_CLEAR = 0.25;  // зазор с каждой стороны модуля
HR_HOLE  = 4.25;  // квадратное отверстие под lockpin
HR_EAR_T = 2;     // толщина ушка, лежащего на лицевой стороне опоры

// Размер модуля в n юнитов с учётом зазоров.
function hr_span(n) = n * HR_UNIT - 2 * HR_CLEAR;

// Центры клеток сетки поперёк модуля шириной n юнитов, отсчёт от края модуля (z = 0).
function hr_cell_centers(n) = [for (i = [0 : n - 1]) -HR_CLEAR + HR_UNIT / 2 + i * HR_UNIT];

// Квадратное сквозное отверстие под lockpin; ось вдоль X, центр в начале координат.
module hr_pin_hole(depth = 10) {
    cube([depth, HR_HOLE, HR_HOLE], center = true);
}

// Крепление «коробки на фасад» между двумя горизонтальными опорами.
//
// Система координат (совпадает с печатью — коробка лежит на столе):
//   X — глубина стойки; лицевой торец коробки (порты) в x = 0, коробка уходит в −X;
//   Y — высота в стойке; коробка по центру, y ∈ [−box_h/2, box_h/2];
//   Z — ширина слота; слот z ∈ [0, hr_span(width_units)], коробка прижата к z = 0.
//
// Что строится (с каждой стороны по Y):
//   ушко    — пластина HR_EAR_T в плоскости лицевого торца, от края коробки до края
//             опоры, с отверстиями под lockpin в центрах клеток;
//   косынки  — два треугольных ребра rib_t за ушком (у коробки и у грани опоры),
//             держат ушко на всю ширину слота; на печати верхняя грань под 45° —
//             нависаний нет;
//   подушка  — короткий брусок между косынками в зоне опоры (spacer_depth), высотой
//             fuse_z: упирается в опору, вес коробки ложится на неё, а не на пины;
//   рейка    — ребро вдоль стенки коробки на fuse_depth вглубь, высотой fuse_z,
//             заходит в стенку на fuse_overlap — этим крепление сваривается с корпусом.
//
// box_h         — высота коробки в стойке (по Y);
// gap_units     — просвет между опорами в юнитах (коробка проходит через него);
// width_units   — ширина модуля в юнитах;
// spacer_depth  — глубина подушки за ушком (не больше глубины опоры, 15 мм);
// fuse_z        — высота вплавляемой части (толщина половинки корпуса);
// fuse_depth    — длина сварки вдоль коробки от лицевого торца; не заводить на вырезы;
// rib_t         — толщина косынок и рейки;
// gusset_depth  — длина косынки по низу (по умолчанию = ширине слота, т.е. 45°);
// fuse_overlap  — насколько сварка заходит в стенку коробки;
// box_clear     — зазор от крепления до коробки выше fuse_z (там стоит невплавляемая
//                 половинка; с запасом на «слоновью ногу» её кромки);
// chamfer_fill  — [высота, глубина] фаски по краю дна коробки, которую рейка заполняет:
//                 иначе под рейкой остаётся щель и слайсер перекрывает её мостом,
//                 а рейка у стола не срастается с коробкой. [0, 0] — без заполнения.
module hr_front_mount(box_h, gap_units = 5, width_units = 2,
                      spacer_depth = 13, fuse_z = 9, fuse_depth = 40,
                      rib_t = 2.4, gusset_depth = undef, fuse_overlap = 0.6,
                      box_clear = 0.5, chamfer_fill = [0, 0]) {
    w      = hr_span(width_units);
    g      = is_undef(gusset_depth) ? w : gusset_depth;
    y_box  = box_h / 2 + box_clear;                   // зазор до коробки (до второй половинки)
    y_gap  = gap_units * HR_UNIT / 2 - HR_CLEAR;      // внутренняя грань опоры
    y_ear  = (gap_units / 2 + 1) * HR_UNIT - HR_CLEAR; // внешний край ушка
    y_pin  = (gap_units + 1) * HR_UNIT / 2;            // центр опоры = центр отверстия

    assert(y_gap - y_box >= 2 * rib_t, "коробка не проходит в просвет между опорами — увеличь gap_units");
    assert(spacer_depth <= HR_UNIT, "подушка глубже опоры");

    // Треугольное ребро в плоскости XZ толщиной rib_t, от y0 вверх по Y.
    module gusset(y0)
        translate([0, y0 + rib_t, 0]) rotate([90, 0, 0]) linear_extrude(rib_t)
            polygon([[0, 0], [0, w], [-HR_EAR_T, w], [-HR_EAR_T - g, 0]]);

    for (s = [-1, 1]) mirror([0, s < 0 ? 1 : 0, 0]) {
        difference() {
            union() {
                // ушко
                translate([-HR_EAR_T, y_box, 0]) cube([HR_EAR_T, y_ear - y_box, w]);
                // косынки
                gusset(y_box);
                gusset(y_gap - rib_t);
                // подушка
                translate([-HR_EAR_T - spacer_depth, y_box, 0])
                    cube([spacer_depth, y_gap - y_box, fuse_z]);
                // рейка-сварка вдоль стенки коробки
                translate([-fuse_depth, box_h / 2 - fuse_overlap, 0])
                    cube([fuse_depth, y_box + rib_t - box_h / 2 + fuse_overlap, fuse_z]);
                // заполнение фаски дна под рейкой
                if (chamfer_fill[0] > 0)
                    translate([-fuse_depth, box_h / 2 - chamfer_fill[1], 0])
                        cube([fuse_depth, chamfer_fill[1], chamfer_fill[0]]);
            }
            for (zc = hr_cell_centers(width_units))
                translate([-HR_EAR_T / 2, y_pin, zc]) hr_pin_hole(HR_EAR_T + 2);
        }
    }
}
