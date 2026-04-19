"""Distribute CADManem rendered videos to matching equation repos.

For each (scene -> equation_id) pair:
  1. Ensure the local repo exists (clone with gh if missing).
  2. Copy the highest-quality MP4 into <repo>/images/<scene>.mp4.
  3. Generate an autoplay-friendly GIF via two-pass ffmpeg palette and
     write to <repo>/images/<scene>.gif.
  4. Insert/refresh a "Hero animation" block at the top of README.md
     embedding the GIF and linking the MP4.
  5. Stage, commit, and push.

Idempotent: if README already contains the marker block, it is replaced.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

WORKSPACE = Path(r"C:\Users\RDM3D\clawdad42")
CADMANEM_VIDEOS = Path(r"C:\Users\RDM3D\CADManem\media\videos")
FFMPEG = r"C:\Users\RDM3D\AppData\Local\ffmpeg\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"

MARKER_BEGIN = "<!-- HERO_ANIMATION:BEGIN -->"
MARKER_END = "<!-- HERO_ANIMATION:END -->"

# Curated, high-confidence scene -> equation_id pairs.
MAPPING: list[tuple[str, str, str]] = [
    # (scene_folder, equation_id, human caption)
    ("adaptive_chern_self_healing", "eq-adaptive-chern-self-healing-conductance-law",
     "Adaptive Chern self-healing conductance law"),
    ("adler_phase_dynamics", "eq-paper1-adler-rsj-phase",
     "Adler / RSJ phase dynamics"),
    ("arp_parity_lock", "eq-paper1-activity-closure",
     "Activity closure A = G|sinφ| — parity lock"),
    ("entropy_gated_edge_recovery", "eq-entropy-gated-edge-recovery-score",
     "Entropy-gated edge recovery score"),
    ("flat_channel_loop_signature", "eq-flat-channel-loop-signature-pi-f-health-observable",
     "Flat-channel loop signature (π_f health observable)"),
    ("flat_inverse_square_normal_form", "eq-flat-adaptive-inverse-square-normal-form-with-kelvin-mel",
     "Flat-adaptive inverse-square normal form"),
    ("landauer_phase_lift", "eq-landauer-phase-lift-conductance-law",
     "Landauer phase-lift conductance law"),
    ("loop_memory_conductance_3d", "eq-loop-coherence-and-curve-memory-stabilized-bz-conductanc",
     "Loop-coherence + curve-memory stabilised BZ conductance"),
    ("phase_lifted_rg_flow", "eq-phase-lifted-rg-memory-flow",
     "Phase-lifted RG memory flow"),
    ("phase_lifted_thouless_pump", "eq-phase-lifted-thouless-pump-memory-law",
     "Phase-lifted Thouless pump memory law"),
    ("pi_f_anticipatory_self_healing", "eq-history-resolved-pif-anticipatory-self-healing-law",
     "History-resolved π_f anticipatory self-healing law"),
    ("qwz_chern_insulator", "eq-paper1-qwz-hamiltonian",
     "QWZ Chern insulator Hamiltonian"),
    ("self_healing_lattice", "eq-flat-channel-deficit-gated-self-healing-law",
     "Flat-channel deficit-gated self-healing lattice"),
    ("topological_coherence", "eq-topological-coherence-order-parameter-arp-locking",
     "Topological coherence order parameter (ARP locking)"),
    ("topological_self_healing", "eq-adaptive-topological-self-healing-conductance-law",
     "Adaptive topological self-healing conductance law"),
    ("kelvin_mellin_beta_manifold", "eq-flat-adaptive-inverse-square-normal-form-with-kelvin-mel",
     "Kelvin–Mellin β-manifold (companion view)"),  # secondary asset for same repo
]


@dataclass
class Job:
    scene: str
    repo: str
    caption: str
    mp4_src: Path
    is_secondary: bool = False  # if true, do not overwrite hero block, just add asset

    @property
    def repo_path(self) -> Path:
        return WORKSPACE / self.repo

    @property
    def images_dir(self) -> Path:
        return self.repo_path / "images"

    @property
    def mp4_dst(self) -> Path:
        return self.images_dir / f"{self.scene}.mp4"

    @property
    def gif_dst(self) -> Path:
        return self.images_dir / f"{self.scene}.gif"


def find_best_mp4(scene: str) -> Path | None:
    folder = CADMANEM_VIDEOS / scene
    if not folder.is_dir():
        return None
    best: tuple[int, Path] | None = None
    for path in folder.rglob("*.mp4"):
        if "partial_movie_files" in path.parts:
            continue
        rank = 3 if "1080p60" in path.parts else (1 if "480p15" in path.parts else 2)
        if best is None or rank > best[0]:
            best = (rank, path)
    return best[1] if best else None


def run(cmd: list[str], cwd: Path | None = None, check: bool = True,
        capture: bool = False) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(str(c) for c in cmd)}", flush=True)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
    )


def ensure_repo(job: Job) -> bool:
    if job.repo_path.is_dir() and (job.repo_path / ".git").is_dir():
        return True
    print(f"[clone] {job.repo}")
    try:
        run(["git", "clone", f"https://github.com/RDM3DC/{job.repo}.git",
             str(job.repo_path)])
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  ! clone failed: {exc}")
        return False


def make_gif(mp4: Path, gif_out: Path, *, fps: int = 12, width: int = 540) -> None:
    palette = gif_out.with_suffix(".palette.png")
    vf_pal = f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=stats_mode=full"
    vf_use = (f"fps={fps},scale={width}:-1:flags=lanczos [x]; "
              f"[x][1:v] paletteuse=dither=bayer:bayer_scale=5")
    run([FFMPEG, "-y", "-i", str(mp4), "-vf", vf_pal, str(palette)],
        capture=True)
    run([FFMPEG, "-y", "-i", str(mp4), "-i", str(palette),
         "-lavfi", vf_use, "-loop", "0", str(gif_out)], capture=True)
    palette.unlink(missing_ok=True)


def update_readme(job: Job) -> bool:
    readme = job.repo_path / "README.md"
    rel_gif = f"images/{job.scene}.gif"
    rel_mp4 = f"images/{job.scene}.mp4"
    block = (
        f"{MARKER_BEGIN}\n"
        f"![{job.caption}]({rel_gif})\n\n"
        f"_Hero animation: **{job.caption}**. "
        f"[Download high-resolution MP4]({rel_mp4})._\n"
        f"{MARKER_END}\n"
    )
    if not readme.exists():
        readme.write_text(f"# {job.repo}\n\n{block}\n", encoding="utf-8")
        return True
    text = readme.read_text(encoding="utf-8")
    if MARKER_BEGIN in text and MARKER_END in text:
        pre, _, rest = text.partition(MARKER_BEGIN)
        _, _, post = rest.partition(MARKER_END)
        new_text = f"{pre.rstrip()}\n\n{block}\n{post.lstrip()}"
    else:
        # Insert after first heading if present, else prepend.
        lines = text.splitlines(keepends=True)
        insert_at = 0
        for i, ln in enumerate(lines):
            if ln.startswith("# "):
                insert_at = i + 1
                # also skip a single blank after the H1
                if insert_at < len(lines) and lines[insert_at].strip() == "":
                    insert_at += 1
                break
        new_lines = lines[:insert_at] + ["\n", block, "\n"] + lines[insert_at:]
        new_text = "".join(new_lines)
    if new_text == text:
        return False
    readme.write_text(new_text, encoding="utf-8")
    return True


def git_status(repo_path: Path) -> str:
    cp = run(["git", "-C", str(repo_path), "status", "--porcelain"], capture=True)
    return cp.stdout


def commit_and_push(job: Job) -> bool:
    repo = job.repo_path
    status = git_status(repo)
    if not status.strip():
        print("  (no changes)")
        return False
    run(["git", "-C", str(repo), "add", "-A"])
    msg = f"Add hero animation: {job.scene} ({job.caption})"
    try:
        run(["git", "-C", str(repo), "commit", "-m", msg])
    except subprocess.CalledProcessError as exc:
        print(f"  ! commit failed: {exc}")
        return False
    try:
        run(["git", "-C", str(repo), "push"])
    except subprocess.CalledProcessError as exc:
        print(f"  ! push failed: {exc}")
        return False
    return True


def process(job: Job, *, do_push: bool) -> dict:
    print(f"\n=== {job.scene} -> {job.repo} ===")
    result = {"scene": job.scene, "repo": job.repo, "ok": False, "note": ""}
    if not job.mp4_src.exists():
        result["note"] = "source mp4 missing"
        print(f"  ! {result['note']}: {job.mp4_src}")
        return result
    if not ensure_repo(job):
        result["note"] = "repo clone failed"
        return result
    job.images_dir.mkdir(parents=True, exist_ok=True)

    # Copy MP4
    if (not job.mp4_dst.exists()
            or job.mp4_dst.stat().st_size != job.mp4_src.stat().st_size):
        shutil.copy2(job.mp4_src, job.mp4_dst)
        print(f"  copied mp4 ({job.mp4_src.stat().st_size/1_048_576:.2f} MB)")

    # Generate GIF
    if not job.gif_dst.exists():
        try:
            make_gif(job.mp4_src, job.gif_dst)
            print(f"  built gif ({job.gif_dst.stat().st_size/1_048_576:.2f} MB)")
        except subprocess.CalledProcessError as exc:
            result["note"] = f"ffmpeg failed: {exc}"
            print(f"  ! {result['note']}")
            return result

    # README
    if not job.is_secondary:
        if update_readme(job):
            print("  updated README hero block")
        else:
            print("  README already current")
    else:
        print("  (secondary asset; README not modified)")

    # Commit + push
    if do_push:
        pushed = commit_and_push(job)
        result["ok"] = True
        result["note"] = "pushed" if pushed else "no changes"
    else:
        result["ok"] = True
        result["note"] = "staged (no push)"
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-push", action="store_true", help="Stage files but skip git push")
    ap.add_argument("--only", help="Run only this scene name")
    args = ap.parse_args()

    secondary = {"kelvin_mellin_beta_manifold"}
    jobs: list[Job] = []
    for scene, repo, caption in MAPPING:
        if args.only and scene != args.only:
            continue
        mp4 = find_best_mp4(scene)
        if mp4 is None:
            print(f"[skip] no mp4 for {scene}")
            continue
        jobs.append(Job(scene=scene, repo=repo, caption=caption,
                        mp4_src=mp4, is_secondary=(scene in secondary)))

    results = []
    for job in jobs:
        results.append(process(job, do_push=not args.no_push))

    print("\n\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r["ok"] else "ERR"
        print(f"  {flag}  {r['repo']:<60s}  ({r['scene']})  {r['note']}")
    failed = [r for r in results if not r["ok"]]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
