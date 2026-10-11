// pi4b-case-mount.scad — нижняя половинка корпуса BTT CB1 + PI4B adapter с ушками HomeRacker.
//
// Корпус стоит ребром, портами USB/Ethernet наружу, уходит вглубь стойки на 90.5 мм.
// Модуль: 2 юнита по ширине, просвет 5 юнитов между горизонтальными опорами
// (с ушками — 7 юнитов по фасаду). Верхняя половинка корпуса не меняется.
//
// STL половинок вытаскиваются из исходного 3MF скриптом tools/3mf_to_stl.py.
// Подробности и порядок сборки — в README.md рядом.

use <homeracker.scad>

/* [Файлы] */
case_dir = "D:/3d projects/2026-10-11-pi4b-homeracker";

/* [Что строить] */
// case — нижняя половинка с креплением; test — одно ушко для проверки посадки пина
part = "case"; // [case, test]
// показать верхнюю половинку полупрозрачной (только превью F5)
show_top = true;

/* [Крепление] */
gap_units    = 5;
width_units  = 2;
spacer_depth = 13;
// длина сварки вдоль корпуса от торца портов; вырезы USB-C/HDMI начинаются с 45 мм
fuse_depth   = 40;

/* [Hidden] */
// Габариты корпуса, снятые с мешей (мм).
CASE_L   = 90.5;  // длина (глубина в стойке), порты на торце +X меша
CASE_H   = 62;    // ширина платы = высота в стойке
BOTTOM_T = 9.4;   // толщина нижней половинки (меш z ∈ [−4.7, 4.7])
TOP_T    = 10;    // толщина верхней половинки (меш z ∈ [−5, 5])

// Перевод из координат меша в координаты крепления: торец портов в x = 0, дно на z = 0.
module place_bottom() translate([-CASE_L / 2, 0, BOTTOM_T / 2]) children();
module place_top()    translate([-CASE_L / 2, 0, BOTTOM_T + TOP_T / 2]) children();

if (part == "case") {
    place_bottom() import(str(case_dir, "/pi4b-bottom-m25-nuts.stl"), convexity = 10);
    hr_front_mount(CASE_H, gap_units, width_units, spacer_depth,
                   fuse_z = BOTTOM_T, fuse_depth = fuse_depth);
    if (show_top)
        %place_top() import(str(case_dir, "/pi4b-top.stl"), convexity = 10);
} else {
    // Тестовое ушко: одна сторона крепления без корпуса, рейка укорочена до подушки.
    intersection() {
        hr_front_mount(CASE_H, gap_units, width_units, spacer_depth,
                       fuse_z = BOTTOM_T, fuse_depth = spacer_depth + 2);
        translate([-50, 0, -1]) cube([100, 100, 100]);
    }
}
