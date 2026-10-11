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
//   ушко   — пластина HR_EAR_T в плоскости лицевого торца, от края коробки до края
//            опоры, с отверстиями под lockpin в центрах клеток;
//   проставка — брусок за ушком, заполняет щель между коробкой и опорой;
//              вес коробки ложится на нижнюю опору, а не на пины;
//   сварка — полоска, заходящая на fuse_overlap в стенку коробки по высоте fuse_z
//            (той половинки, в которую вплавляем), чтобы крепление срослось с ней.
//
// box_h         — высота коробки в стойке (по Y);
// gap_units     — просвет между опорами в юнитах (коробка проходит через него);
// width_units   — ширина модуля в юнитах;
// spacer_depth  — глубина проставки за ушком;
// fuse_z        — высота вплавляемой части (толщина половинки корпуса);
// fuse_overlap  — насколько сварка заходит в стенку коробки.
module hr_front_mount(box_h, gap_units = 5, width_units = 2,
                      spacer_depth = 13, fuse_z = 0, fuse_overlap = 0.6) {
    w      = hr_span(width_units);
    y_box  = box_h / 2 + HR_CLEAR;                    // зазор до коробки (до второй половинки)
    y_gap  = gap_units * HR_UNIT / 2 - HR_CLEAR;      // внутренняя грань опоры
    y_ear  = (gap_units / 2 + 1) * HR_UNIT - HR_CLEAR; // внешний край ушка
    y_pin  = (gap_units + 1) * HR_UNIT / 2;            // центр опоры = центр отверстия
    x_back = -HR_EAR_T - spacer_depth;

    assert(y_gap > y_box, "коробка не проходит в просвет между опорами — увеличь gap_units");

    for (s = [-1, 1]) mirror([0, s < 0 ? 1 : 0, 0]) {
        difference() {
            union() {
                // ушко
                translate([-HR_EAR_T, y_box, 0]) cube([HR_EAR_T, y_ear - y_box, w]);
                // проставка
                translate([x_back, y_box, 0]) cube([spacer_depth, y_gap - y_box, w]);
                // сварка с корпусом
                if (fuse_z > 0)
                    translate([x_back, box_h / 2 - fuse_overlap, 0])
                        cube([-x_back, y_box - box_h / 2 + fuse_overlap + 0.01, fuse_z]);
            }
            for (zc = hr_cell_centers(width_units))
                translate([-HR_EAR_T / 2, y_pin, zc]) hr_pin_hole(HR_EAR_T + 2);
        }
    }
}
