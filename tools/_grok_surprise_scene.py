"""Manim animation for the Grok Surprise-Augmented Phase-Lifted Entropy-Gated
Conductance Update equation.

Renders a ~15s 1080p60 scene showing:
  1. Title + equation write-in
  2. Phase-space plot: conductance magnitude |G| vs time with/without surprise
  3. Surprise signal U(t) = 1 - |cos(Δφ(t))| pulsing
  4. Key insight: U→0 recovers the #1 entropy-gated law

Usage:
  manim -pqh --fps 60 tools/_grok_surprise_scene.py GrokSurpriseScene
  # or for production:
  manim -qh --fps 60 -o GrokSurpriseAnimation.mp4 tools/_grok_surprise_scene.py GrokSurpriseScene
"""
from manim import *
import numpy as np


class GrokSurpriseScene(Scene):
    def construct(self):
        # ---- Parameters ----
        kappa = 0.3
        eta = 0.25
        alpha_base = 0.8
        mu_base = 0.15
        dt = 0.02
        steps = 500

        # ---- Simulate two trajectories ----
        # Phase difference: starts misaligned, gradually locks
        t_arr = np.arange(steps) * dt
        delta_phi = 1.2 * np.exp(-0.3 * t_arr) * np.sin(2.5 * t_arr) + 0.4 * np.exp(-0.15 * t_arr)
        U = 1.0 - np.abs(np.cos(delta_phi))  # surprise signal
        I_mag = 0.6 + 0.3 * np.sin(1.5 * t_arr)  # driving current magnitude

        # With surprise
        G_surprise = np.zeros(steps)
        G_surprise[0] = 0.1
        for i in range(1, steps):
            reinforce = alpha_base * (1 + kappa * U[i]) * I_mag[i]
            decay = mu_base * (1 - eta * U[i]) * G_surprise[i - 1]
            G_surprise[i] = max(0, G_surprise[i - 1] + dt * (reinforce - decay))

        # Without surprise (U=0, recovers #1 law)
        G_base = np.zeros(steps)
        G_base[0] = 0.1
        for i in range(1, steps):
            reinforce = alpha_base * I_mag[i]
            decay = mu_base * G_base[i - 1]
            G_base[i] = max(0, G_base[i - 1] + dt * (reinforce - decay))

        # Normalize for plotting
        t_max = t_arr[-1]
        G_max = max(G_surprise.max(), G_base.max()) * 1.1

        # ---- Scene ----
        # 1. Title
        title = Text("Grok Surprise-Augmented", font_size=40, color=WHITE)
        subtitle = Text("Phase-Lifted Entropy-Gated Conductance", font_size=32, color=BLUE_B)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.3)

        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.6)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.5)

        # 2. Equation
        eq = MathTex(
            r"\frac{d\tilde{G}_{ij}}{dt}",
            r"=",
            r"\alpha_G(S)",
            r"\,(1+\kappa U_{ij})",
            r"\,|I_{ij}|\,e^{i\theta_R}",
            r"-",
            r"\mu_G(S)",
            r"\,(1-\eta U_{ij})",
            r"\,\tilde{G}_{ij}",
            font_size=36,
        )
        eq.next_to(title_group, DOWN, buff=0.35)

        self.play(Write(eq), run_time=2.0)
        self.wait(0.5)

        # Highlight surprise terms
        box1 = SurroundingRectangle(eq[3], color=YELLOW, buff=0.06)
        box2 = SurroundingRectangle(eq[7], color=YELLOW, buff=0.06)
        lbl = Text("← Surprise gates", font_size=22, color=YELLOW)
        lbl.next_to(box2, RIGHT, buff=0.15)
        self.play(Create(box1), Create(box2), FadeIn(lbl), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(box1), FadeOut(box2), FadeOut(lbl), run_time=0.5)

        # Shift equation + title up
        top_group = VGroup(title_group, eq)
        self.play(top_group.animate.scale(0.8).to_edge(UP, buff=0.15), run_time=0.6)

        # 3. Two-panel plot area
        # Left: Conductance |G| vs time
        ax_g = Axes(
            x_range=[0, t_max, 2],
            y_range=[0, G_max, round(G_max / 4, 1)],
            x_length=5.5,
            y_length=3.0,
            tips=False,
            axis_config={"include_numbers": False, "stroke_width": 2},
        )
        ax_g.shift(LEFT * 3.2 + DOWN * 1.0)
        g_title = Text("|G(t)| — Conductance", font_size=20, color=WHITE)
        g_title.next_to(ax_g, UP, buff=0.12)
        x_lbl_g = Text("t", font_size=18).next_to(ax_g.x_axis, RIGHT, buff=0.1)
        y_lbl_g = Text("|G|", font_size=18).next_to(ax_g.y_axis, UP, buff=0.1)

        # Right: Surprise U(t)
        ax_u = Axes(
            x_range=[0, t_max, 2],
            y_range=[0, 1.1, 0.5],
            x_length=5.5,
            y_length=3.0,
            tips=False,
            axis_config={"include_numbers": False, "stroke_width": 2},
        )
        ax_u.shift(RIGHT * 3.2 + DOWN * 1.0)
        u_title = Text("U(t) — Surprise Signal", font_size=20, color=YELLOW)
        u_title.next_to(ax_u, UP, buff=0.12)
        x_lbl_u = Text("t", font_size=18).next_to(ax_u.x_axis, RIGHT, buff=0.1)
        y_lbl_u = Text("U", font_size=18).next_to(ax_u.y_axis, UP, buff=0.1)

        self.play(
            FadeIn(ax_g), FadeIn(g_title), FadeIn(x_lbl_g), FadeIn(y_lbl_g),
            FadeIn(ax_u), FadeIn(u_title), FadeIn(x_lbl_u), FadeIn(y_lbl_u),
            run_time=0.8,
        )

        # Plot curves
        def _make_curve(ax, t, y, color):
            points = [ax.c2p(t[i], y[i]) for i in range(len(t))]
            return VMobject(color=color, stroke_width=2.5).set_points_smoothly(points)

        curve_base = _make_curve(ax_g, t_arr, G_base, BLUE_C)
        curve_surp = _make_curve(ax_g, t_arr, G_surprise, GREEN_B)
        curve_u = _make_curve(ax_u, t_arr, U, YELLOW)

        # Legend
        leg_base = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=BLUE_C, stroke_width=3),
            Text("U=0 (#1 law)", font_size=16, color=BLUE_C),
        ).arrange(RIGHT, buff=0.1)
        leg_surp = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=GREEN_B, stroke_width=3),
            Text("With surprise", font_size=16, color=GREEN_B),
        ).arrange(RIGHT, buff=0.1)
        legend = VGroup(leg_base, leg_surp).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        legend.next_to(ax_g, DOWN, buff=0.2).align_to(ax_g, LEFT)

        # Animate curves drawing simultaneously
        self.play(
            Create(curve_base, run_time=3.0, rate_func=linear),
            Create(curve_surp, run_time=3.0, rate_func=linear),
            Create(curve_u, run_time=3.0, rate_func=linear),
        )
        self.play(FadeIn(legend), run_time=0.5)

        self.wait(0.5)

        # 4. Key insight callout
        insight_box = RoundedRectangle(
            width=10, height=0.7, corner_radius=0.15, color=GREEN, fill_opacity=0.15
        )
        insight_box.to_edge(DOWN, buff=0.2)
        insight_text = Text(
            "When U → 0 (perfect phase lock), exactly recovers the #1 entropy-gated law",
            font_size=20,
            color=GREEN_A,
        )
        insight_text.move_to(insight_box)

        self.play(FadeIn(insight_box), Write(insight_text), run_time=1.2)
        self.wait(2.5)

        # Fade all
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
