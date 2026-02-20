
from manim import *

class AutoEquation(Scene):
    def construct(self):
        title = Text('ARP Lyapunov Stability Form', font_size=44)
        title.to_edge(UP)

        eq = MathTex('V(x)\\ge 0,\\ V(0)=0;\\ \\dot V(x)=\\nabla V\\cdot \\dot x\\le -\\alpha V(x)').scale(1.15)
        eq.next_to(title, DOWN, buff=0.6)

        desc = Text('Candidate stability proof template for adaptive conductance dynamics.', font_size=26)
        desc.set_color(BLUE_A)
        desc.next_to(eq, DOWN, buff=0.55)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(Write(eq), run_time=1.4)
        self.play(FadeIn(desc, shift=DOWN), run_time=1.0)

        box = SurroundingRectangle(eq, color=GREEN, buff=0.18)
        self.play(Create(box), run_time=0.6)
        self.wait(0.7)
        self.play(FadeOut(box), run_time=0.5)
        self.wait(1.0)
