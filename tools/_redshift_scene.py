from manim import *
import numpy as np


class AutoEquation(Scene):
    def construct(self):
        title = Text("ARP Redshift Law (derived mapping)", font_size=52)
        title.to_edge(UP)

        eq = MathTex(r"z(t)=z_0\,(1-e^{-\gamma t})").scale(1.22)
        eq.next_to(title, DOWN, buff=0.5)

        what = Text(
            "Exponential relaxation expressed as a normalized deficit observable.",
            font_size=30,
            color=BLUE_A,
        )
        what.next_to(eq, DOWN, buff=0.35)

        legend_title = Text("Bridge from ARP", font_size=28, color=GRAY_A)
        bridge = VGroup(
            MathTex(r"\dot G = -\mu\,(G-G_\infty)"),
            MathTex(r"G(t)=G_\infty+(G_0-G_\infty)e^{-\mu t}"),
            MathTex(
                r"z:=z_0\Big(1-\frac{G-G_\infty}{G_0-G_\infty}\Big)\Rightarrow z=z_0(1-e^{-\mu t})"
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).scale(0.72)
        legend = VGroup(legend_title, bridge).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        legend.to_corner(DL)

        pred_title = Text("Prediction", font_size=28, color=GRAY_A)
        pred = Text("Monotone rise to z0 with half-time t1/2 = ln2/γ (γ>0).", font_size=28)
        pred_box = VGroup(pred_title, pred).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        pred_box.to_corner(DR)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(Write(eq), run_time=2.0)
        self.play(FadeIn(what, shift=DOWN), run_time=1.1)
        self.play(FadeIn(legend, shift=UP), FadeIn(pred_box, shift=UP), run_time=1.4)

        # Demo: G(t) decays while z(t) rises; show mapping live
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 1.05, 0.25], tips=False).scale(0.72)
        axes.to_edge(DOWN)
        xlab = axes.get_x_axis_label(MathTex(r"t"), edge=RIGHT, direction=RIGHT).scale(0.9)
        ylab = axes.get_y_axis_label(MathTex(r"\text{normalized}"), edge=UP, direction=UP).scale(0.9)

        mu = 0.55
        G = lambda t: np.exp(-mu * t)  # (G-Ginf)/(G0-Ginf)
        z = lambda t: 1 - np.exp(-mu * t)  # z/z0

        g_curve = axes.plot(lambda t: G(t), x_range=[0, 10], color=GREEN)
        z_curve = axes.plot(lambda t: z(t), x_range=[0, 10], color=YELLOW)
        g_lbl = Text("(G-G∞)/(G0-G∞)", font_size=22, color=GREEN).next_to(axes, LEFT, buff=0.25).shift(UP * 0.2)
        z_lbl = Text("z/z0", font_size=22, color=YELLOW).next_to(g_lbl, DOWN, buff=0.18)

        t = ValueTracker(0.0)
        g_dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), G(t.get_value())), radius=0.06, color=GREEN))
        z_dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), z(t.get_value())), radius=0.06, color=YELLOW))

        map_txt = always_redraw(
            lambda: MathTex(
                r"z/z_0 = 1-(G-G_\infty)/(G_0-G_\infty)",
                font_size=30,
            )
            .to_edge(UP)
            .shift(DOWN * 0.85)
        )

        self.play(FadeIn(axes), FadeIn(xlab), FadeIn(ylab), run_time=1.0)
        self.play(Create(g_curve), Create(z_curve), FadeIn(g_lbl), FadeIn(z_lbl), run_time=1.5)
        self.play(FadeIn(g_dot), FadeIn(z_dot), FadeIn(map_txt), run_time=0.8)
        self.play(t.animate.set_value(10.0), run_time=10.0, rate_func=smooth)
        self.wait(5.0)
