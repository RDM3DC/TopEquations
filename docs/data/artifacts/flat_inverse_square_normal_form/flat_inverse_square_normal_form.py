"""Flat-adaptive inverse-square normal form and Hardy corollary.

Submission-oriented explainer for the exact half-density reduction of the
power-law flat-adaptive radial operator.

Scenes
------
FlatInverseSquareNormalForm
    Main animation: power-law branch -> half-density conjugation -> inverse-square
    potential -> eigenvalue form -> Hardy corollary.

FlatInverseSquarePotentialPlot
    Static plot card for V_beta(r) = (beta^2 - 1)/(4 r^2) across representative
    beta values. Useful as a submission attachment.

Run
---
    manim -pql examples/flat_inverse_square_normal_form.py FlatInverseSquareNormalForm
    manim -s -ql examples/flat_inverse_square_normal_form.py FlatInverseSquarePotentialPlot
"""

from __future__ import annotations

import numpy as np
from manim import (
    Axes,
    DecimalNumber,
    DOWN,
    FadeIn,
    FadeOut,
    GREEN,
    GREY_A,
    GREY_B,
    LEFT,
    MathTex,
    ORANGE,
    RED,
    RIGHT,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    TEAL,
    Text,
    Transform,
    UP,
    ValueTracker,
    VGroup,
    WHITE,
    Write,
    YELLOW,
    always_redraw,
    Create,
    LaggedStart,
    AnimationGroup,
    Indicate,
    BLUE,
    GOLD,
    ManimColor,
    interpolate_color,
)


BG = "#07141D"
PANEL = "#0F2331"
GRID = "#2B5A75"
SOFT = "#91A8B8"
ACCENT = GOLD
PI_F = YELLOW
OP_COL = TEAL
POT_COL = ORANGE
HARDY_COL = GREEN
WARN = RED
FREE = BLUE
CRITICAL = ManimColor("#4FD1C5")


def _panel(width: float, height: float, color=GRID, opacity: float = 0.96):
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        fill_color=PANEL,
        fill_opacity=opacity,
        stroke_color=color,
        stroke_width=1.45,
    )


def _beta_color(beta: float) -> ManimColor:
    if beta <= -1.0:
        return FREE
    if beta < 0.0:
        return interpolate_color(FREE, CRITICAL, (beta + 1.0) / 1.0)
    if beta < 1.0:
        return interpolate_color(CRITICAL, PI_F, beta)
    return interpolate_color(PI_F, WARN, min(1.0, (beta - 1.0) / 1.2))


def _potential(r_value: float, beta: float) -> float:
    return (beta * beta - 1.0) / (4.0 * r_value * r_value)


def _clipped_potential(r_value: float, beta: float, y_clip: float = 2.4) -> float:
    return float(np.clip(_potential(r_value, beta), -y_clip, y_clip))


def _branch_label(beta: float) -> tuple[str, ManimColor]:
    if abs(beta + 1.0) < 1e-8:
        return "FREE BRANCH  beta = -1", FREE
    if abs(beta) < 1e-8:
        return "CRITICAL LOG BRANCH  beta = 0", CRITICAL
    if abs(beta) < 1.0:
        return "ATTRACTIVE INVERSE-SQUARE WELL", POT_COL
    return "REPULSIVE INVERSE-SQUARE BARRIER", WARN


def _potential_axes() -> tuple[Axes, Text, Text]:
    axes = Axes(
        x_range=[0.35, 3.3, 0.5],
        y_range=[-2.4, 2.4, 1.0],
        x_length=5.6,
        y_length=3.5,
        axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18},
        tips=False,
    )
    x_label = Text("r", font_size=20, color=WHITE).next_to(axes.x_axis, RIGHT, buff=0.18)
    y_label = MathTex(r"V_\beta(r)", font_size=28, color=POT_COL).next_to(axes.y_axis, UP, buff=0.18)
    return axes, x_label, y_label


class FlatInverseSquareNormalForm(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = Text("Flat-Adaptive Inverse-Square Normal Form", font_size=38, color=ACCENT)
        subtitle = Text("exact half-density reduction of the power-law flat branch", font_size=19, color=SOFT)
        subtitle.next_to(title, DOWN, buff=0.14)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.08))

        law = MathTex(
            r"\pi_f(r)=\pi\lambda_0\!\left(\frac{r}{r_0}\right)^{\beta}",
            font_size=34,
            color=PI_F,
        )
        weight = MathTex(
            r"w_f(r)=2\pi\lambda_0 r_0^{-\beta}r^{\beta+1}",
            font_size=32,
            color=WHITE,
        )
        operator = MathTex(
            r"\Delta_f^{\mathrm{rad}}u=\frac{1}{w_f}\frac{d}{dr}\!\left(w_fu_r\right)",
            font_size=31,
            color=OP_COL,
        )
        drift = MathTex(
            r"=u''+\frac{\beta+1}{r}u'",
            font_size=31,
            color=OP_COL,
        )
        intro = VGroup(law, weight, operator, drift).arrange(DOWN, buff=0.26)
        intro.shift(UP * 0.2)

        self.play(Write(law))
        self.play(Write(weight))
        self.play(Write(operator))
        self.play(Write(drift))

        punch = Text("power law turns the radial drift into a single beta-charge", font_size=20, color=SOFT)
        punch.next_to(intro, DOWN, buff=0.34)
        self.play(FadeIn(punch, shift=UP * 0.08))
        self.wait(0.5)

        conj = MathTex(
            r"\sqrt{w_f}\,\Delta_f^{\mathrm{rad}}\!\left(w_f^{-1/2}\psi\right)",
            r"=",
            r"\psi''-\frac{\beta^2-1}{4r^2}\psi",
            font_size=33,
        )
        conj[0].set_color(OP_COL)
        conj[2].set_color(POT_COL)
        conj_box = SurroundingRectangle(conj, color=ACCENT, buff=0.16, stroke_width=2.0)
        conj_note = Text("half-density conjugation removes the first-order term exactly", font_size=20, color=ACCENT)
        conj_note.next_to(conj, DOWN, buff=0.24)

        self.play(FadeOut(punch, shift=DOWN * 0.06))
        self.play(Transform(intro, conj), run_time=1.25)
        self.play(Create(conj_box), FadeIn(conj_note, shift=UP * 0.06))
        self.wait(0.7)

        eigen = MathTex(
            r"-\psi''+\frac{\beta^2-1}{4r^2}\psi=\kappa^2\psi",
            font_size=34,
            color=WHITE,
        )
        eigen.next_to(conj_note, DOWN, buff=0.3)
        eigen_box = SurroundingRectangle(eigen, color=WHITE, buff=0.15, stroke_width=1.4)
        eigen_tag = Text("standard 1D inverse-square Schrodinger form", font_size=19, color=SOFT)
        eigen_tag.next_to(eigen, DOWN, buff=0.18)

        self.play(Write(eigen), Create(eigen_box))
        self.play(FadeIn(eigen_tag, shift=UP * 0.05))
        self.wait(0.6)

        keep = VGroup(title, subtitle, intro, conj_box, conj_note, eigen, eigen_box, eigen_tag)
        self.play(keep.animate.scale(0.78).to_edge(UP, buff=0.2), run_time=0.9)

        axes, x_label, y_label = _potential_axes()
        axes.to_edge(LEFT, buff=0.55).shift(DOWN * 0.8)
        beta_tracker = ValueTracker(-1.0)

        curve = always_redraw(
            lambda: axes.plot(
                lambda x: _clipped_potential(x, beta_tracker.get_value()),
                x_range=[0.38, 3.2],
                color=_beta_color(beta_tracker.get_value()),
                stroke_width=4,
            )
        )

        curve_fill = always_redraw(
            lambda: axes.get_area(
                curve,
                x_range=[0.38, 3.2],
                color=_beta_color(beta_tracker.get_value()),
                opacity=0.16,
            )
        )

        beta_card = _panel(2.5, 1.25, color=ACCENT)
        beta_card.move_to(RIGHT * 3.25 + DOWN * 0.25)
        beta_label = MathTex(r"\beta =", font_size=29, color=ACCENT)
        beta_label.move_to(beta_card.get_center() + LEFT * 0.42 + UP * 0.14)
        beta_value = DecimalNumber(-1.0, num_decimal_places=2, font_size=28, color=WHITE)
        beta_value.move_to(beta_card.get_center() + RIGHT * 0.38 + UP * 0.14)
        beta_value.add_updater(lambda mob: mob.set_value(beta_tracker.get_value()))

        coeff_label = MathTex(r"\frac{\beta^2-1}{4} =", font_size=22, color=POT_COL)
        coeff_label.move_to(beta_card.get_center() + LEFT * 0.1 + DOWN * 0.3)
        coeff_value = DecimalNumber(0.0, num_decimal_places=2, font_size=22, color=WHITE)
        coeff_value.move_to(beta_card.get_center() + RIGHT * 0.75 + DOWN * 0.3)
        coeff_value.add_updater(lambda mob: mob.set_value((beta_tracker.get_value() ** 2 - 1.0) / 4.0))

        branch_text, branch_color = _branch_label(-1.0)
        branch = Text(branch_text, font_size=20, color=branch_color)
        branch.move_to(RIGHT * 3.2 + DOWN * 1.45)
        branch_box = SurroundingRectangle(branch, color=branch_color, buff=0.12, stroke_width=1.6)

        self.play(FadeIn(axes), FadeIn(x_label), FadeIn(y_label), Create(curve), FadeIn(curve_fill))
        self.play(FadeIn(beta_card), FadeIn(beta_label), FadeIn(beta_value), FadeIn(coeff_label), FadeIn(coeff_value))
        self.play(FadeIn(branch), Create(branch_box))
        self.wait(0.5)

        critical_text, critical_color = _branch_label(0.0)
        critical = Text(critical_text, font_size=20, color=critical_color).move_to(branch)
        critical_box = SurroundingRectangle(critical, color=critical_color, buff=0.12, stroke_width=1.6)

        self.play(beta_tracker.animate.set_value(0.0), run_time=2.2)
        self.play(Transform(branch, critical), Transform(branch_box, critical_box), run_time=0.6)
        self.wait(0.35)

        repulsive_text, repulsive_color = _branch_label(1.8)
        repulsive = Text(repulsive_text, font_size=20, color=repulsive_color).move_to(branch)
        repulsive_box = SurroundingRectangle(repulsive, color=repulsive_color, buff=0.12, stroke_width=1.6)

        self.play(beta_tracker.animate.set_value(1.8), run_time=2.4)
        self.play(Transform(branch, repulsive), Transform(branch_box, repulsive_box), run_time=0.6)
        self.wait(0.5)

        energy_box = _panel(6.3, 2.45, color=HARDY_COL)
        energy_box.move_to(RIGHT * 3.1 + UP * 1.55)
        energy_title = Text("Energy identity", font_size=24, color=HARDY_COL)
        energy_title.move_to(energy_box.get_top() + DOWN * 0.3)
        energy1 = MathTex(
            r"\int_0^\infty w_f|u_r|^2dr=\int_0^\infty |\psi'|^2dr+\frac{\beta^2-1}{4}\int_0^\infty \frac{|\psi|^2}{r^2}dr",
            font_size=24,
            color=WHITE,
        )
        energy1.move_to(energy_box.get_center() + UP * 0.18)
        energy2 = MathTex(
            r"\int |\psi'|^2dr\ge \frac14\int \frac{|\psi|^2}{r^2}dr",
            font_size=24,
            color=ACCENT,
        )
        energy2.move_to(energy_box.get_center() + DOWN * 0.42)

        hardy_box = _panel(6.3, 1.2, color=ACCENT)
        hardy_box.next_to(energy_box, DOWN, buff=0.2)
        hardy = MathTex(
            r"\int_0^\infty w_f|u_r|^2dr\ge \frac{\beta^2}{4}\int_0^\infty \frac{|u|^2}{r^2}w_fdr",
            font_size=28,
            color=HARDY_COL,
        )
        hardy.move_to(hardy_box.get_center())

        self.play(FadeIn(energy_box), FadeIn(energy_title), Write(energy1))
        self.play(Write(energy2))
        self.play(FadeIn(hardy_box), Write(hardy))
        self.play(Indicate(hardy, color=WHITE, scale_factor=1.03), run_time=0.8)
        self.wait(0.6)

        final_group = VGroup(
            axes,
            x_label,
            y_label,
            curve,
            curve_fill,
            beta_card,
            beta_label,
            beta_value,
            coeff_label,
            coeff_value,
            branch,
            branch_box,
            energy_box,
            energy_title,
            energy1,
            energy2,
            hardy_box,
            hardy,
        )
        self.play(FadeOut(final_group), FadeOut(keep), run_time=0.8)

        summary_title = Text("Why this is the stronger flat-pi_f submission", font_size=33, color=ACCENT)
        summary_title.to_edge(UP, buff=0.45)
        summary_items = VGroup(
            MathTex(r"\textbf{1. }\text{Exact: no heuristic closure or fitted term.}", font_size=27, color=WHITE),
            MathTex(r"\textbf{2. }\text{Recognizable spectral problem: inverse-square Schrodinger.}", font_size=27, color=WHITE),
            MathTex(r"\textbf{3. }\text{Same beta controls } d_{\mathrm{eff}},\; V_\beta,\; \text{and Hardy sharpness.}", font_size=27, color=WHITE),
            MathTex(r"\textbf{4. }\beta=-1\ \text{free branch},\quad \beta=0\ \text{critical log branch}.", font_size=27, color=WHITE),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        summary_items.next_to(summary_title, DOWN, buff=0.5)

        footer_box = _panel(10.9, 1.0, color=ACCENT)
        footer_box.to_edge(DOWN, buff=0.36)
        footer = MathTex(
            r"\sqrt{w_f}\,\Delta_f^{\mathrm{rad}}\!\left(w_f^{-1/2}\psi\right)=\psi''-\frac{\beta^2-1}{4r^2}\psi",
            font_size=32,
            color=ACCENT,
        )
        footer.move_to(footer_box.get_center())

        self.play(Write(summary_title))
        self.play(LaggedStart(*[Write(item) for item in summary_items], lag_ratio=0.12))
        self.play(FadeIn(footer_box), Write(footer))
        self.wait(1.8)

        beta_value.clear_updaters()
        coeff_value.clear_updaters()
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class FlatInverseSquarePotentialPlot(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = Text("Potential Family for the Flat-Adaptive Normal Form", font_size=34, color=ACCENT)
        subtitle = MathTex(r"V_\beta(r)=\frac{\beta^2-1}{4r^2}", font_size=34, color=POT_COL)
        subtitle.next_to(title, DOWN, buff=0.16)
        self.add(title, subtitle)

        axes, x_label, y_label = _potential_axes()
        axes.shift(DOWN * 0.3)
        self.add(axes, x_label, y_label)

        beta_specs = [
            (-1.0, FREE, r"\beta=-1\;\text{free}"),
            (0.0, CRITICAL, r"\beta=0\;\text{critical}"),
            (0.6, PI_F, r"\beta=0.6\;\text{attractive}"),
            (2.0, WARN, r"\beta=2\;\text{repulsive}"),
        ]

        curves = VGroup()
        legend_rows = VGroup()
        for beta, color, label in beta_specs:
            curve = axes.plot(
                lambda x, beta=beta: _clipped_potential(x, beta),
                x_range=[0.38, 3.2],
                color=color,
                stroke_width=4,
            )
            curves.add(curve)

            swatch = RoundedRectangle(
                width=0.42,
                height=0.18,
                corner_radius=0.04,
                fill_color=color,
                fill_opacity=1.0,
                stroke_color=color,
                stroke_width=0.0,
            )
            text = MathTex(label, font_size=24, color=WHITE)
            legend_rows.add(VGroup(swatch, text).arrange(RIGHT, buff=0.18))

        legend_rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        legend_panel = _panel(4.6, 2.15, color=ACCENT)
        legend = VGroup(legend_panel, legend_rows)
        legend_panel.move_to(RIGHT * 3.25 + DOWN * 0.1)
        legend_rows.move_to(legend_panel.get_center())

        note_panel = _panel(11.0, 0.9, color=HARDY_COL)
        note_panel.to_edge(DOWN, buff=0.35)
        note = Text(
            "The coefficient changes sign at |beta| = 1; the sharp weighted Hardy constant is beta^2 / 4.",
            font_size=20,
            color=HARDY_COL,
        )
        note.move_to(note_panel.get_center())

        self.add(curves, legend, note_panel, note)