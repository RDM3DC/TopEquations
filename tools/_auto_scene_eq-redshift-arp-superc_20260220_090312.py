
from manim import *

class AutoEquation(Scene):
    def construct(self):
        title = Text('Redshift-ARP Superconductivity Law', font_size=52)
        title.to_edge(UP)

        eq = MathTex('R_s(z) = R_{s,0} (1 + z)^\\alpha').scale(1.25)
        eq.next_to(title, DOWN, buff=0.55)

        what = Text('Proposes a cosmological scaling for critical superconducting resistance: R_s(z) = R_{s,0} (1+z)^alpha. Assumes layered…', font_size=30, color=BLUE_A)
        what.next_to(eq, DOWN, buff=0.45)

        legend_title = Text("Symbols", font_size=28, color=GRAY_A)
        legend = VGroup(*[Text(s, font_size=26) for s in ['α: reinforcement', 'μ: decay', '(see card for assumptions)']]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        legend_box = VGroup(legend_title, legend).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        legend_box.to_corner(DL)

        pred_title = Text("Prediction", font_size=28, color=GRAY_A)
        pred = Text('Simulate + look for a distinctive response curve.', font_size=28)
        pred_box = VGroup(pred_title, pred).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        pred_box.to_corner(DR)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(Write(eq), run_time=1.8)
        self.play(FadeIn(what, shift=DOWN), run_time=1.2)
        self.play(FadeIn(legend_box, shift=UP), FadeIn(pred_box, shift=UP), run_time=1.2)

        box = SurroundingRectangle(eq, color=GREEN, buff=0.18)
        self.play(Create(box), run_time=0.7)
        self.wait(1.3)
        self.play(FadeOut(box), run_time=0.4)

        # Simple demo: animate a generic "response" curve (illustrative)
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 1.2, 0.2], tips=False).scale(0.75)
        axes.to_edge(DOWN)
        xlab = axes.get_x_axis_label(Text("input", font_size=24), edge=RIGHT, direction=RIGHT)
        ylab = axes.get_y_axis_label(Text("response", font_size=24), edge=UP, direction=UP)
        graph = axes.plot(lambda x: 1 - np.exp(-0.55*x), x_range=[0,10], color=YELLOW)
        dot = Dot(axes.c2p(0,0), radius=0.06, color=RED)
        tracker = ValueTracker(0)
        dot.add_updater(lambda m: m.move_to(axes.c2p(tracker.get_value(), 1 - np.exp(-0.55*tracker.get_value()))))

        self.play(FadeIn(axes), FadeIn(xlab), FadeIn(ylab), run_time=0.9)
        self.play(Create(graph), run_time=1.0)
        self.play(FadeIn(dot), run_time=0.4)
        self.play(tracker.animate.set_value(10), run_time=6.0, rate_func=smooth)
        self.wait(2.0)
