# Space Shooter 3D

A 3D space shooter built with **Python** and **PyOpenGL** (GLUT). Pilot a fighter jet, blast through waves of enemies and asteroids, grab power-ups, and take down the boss to win.

Made as a project for **CSE423 – Computer Graphics**.

## Features

- Fully 3D scene with a plane model built from OpenGL primitives (cubes, spheres, cylinders)
- Enemy ships that fly toward you and shoot back
- Asteroids that drift in as hazards
- **Levels** that increase every 50 points, making enemies faster and more numerous
- **Boss fight** at 300 points, with a health bar and an enraged phase below 50% HP
- **Power-ups**
  - Yellow: weapon overcharge (double damage)
  - Blue: shield
  - Pink: extra life
- Particle explosions and a damage flash effect
- First-person and third-person cameras, with camera panning
- Autopilot (cheat) mode
- Scrolling starfield, score, lives and status HUD

## Requirements

- Python 3.8+
- PyOpenGL
- FreeGLUT (needed for GLUT on some systems)

## Installation

```bash
git clone https://github.com/<your-username>/space-shooter-3d.git
cd space-shooter-3d
pip install PyOpenGL PyOpenGL_accelerate
```

**FreeGLUT setup**

- **Windows:** download `freeglut.dll` (for example from the [PyOpenGL wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl) or [freeglut](https://freeglut.sourceforge.net/)) and place it next to the script or in your PATH.
- **Ubuntu/Debian:** `sudo apt install freeglut3-dev`
- **macOS:** GLUT ships with the system.

## Run

```bash
python main.py
```

(Rename `CSE423_Project.py` to `main.py`, or run it under its original name.)

## Controls

| Input | Action |
|-------|--------|
| `W` `A` `S` `D` | Move the plane up / left / down / right |
| `Space` or Left Click | Fire |
| Right Click | Toggle first / third-person camera |
| `F1` | First-person camera |
| `F3` | Third-person camera |
| Arrow keys | Pan the camera (third-person) |
| `Z` | Reset camera pan |
| `C` | Toggle autopilot (cheat mode) |
| `R` | Restart after game over or victory |

## How to Play

1. Shoot enemies (+10) and asteroids (+5) to raise your score.
2. Avoid enemy fire and collisions. You start with 5 lives.
3. Collect power-up boxes as they appear.
4. Reach **300 points** to trigger the boss. Defeat it (+200) to win.
5. Lose all lives and it's mission failed. Press `R` to try again.

## Project Structure

```
.
├── main.py      # entire game: rendering, input, game logic
└── README.md
```

## Tech Notes

- Rendering uses the fixed-function OpenGL pipeline via `OpenGL.GL`, `OpenGL.GLU` and `OpenGL.GLUT`.
- Game state lives in module-level variables and updates in the GLUT `idle` callback.
- Text is drawn with GLUT bitmap fonts through an orthographic overlay.

## License

Add a license of your choice (MIT is a common option for student projects).
