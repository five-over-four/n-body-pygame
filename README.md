# n-body-pygame
N-body simulation in pygame. Supports saving/loading, custom colours, click-drag to shoot, right click to remove masses. Save your own preferences in `settings.json`. Consider lowering trail_length for better performance. `sim_precision` increases numerical accuracy somewhat, but isn't that important in general.

![](https://i.imgur.com/WWlqsLq.png)
## Controls

    Left click and drag to shoot a body in a direction. Just click for no initial velocity.
    Right click to delete a body.
    SPACE to pause and unpause.
    F to toggle camera centering.
    DEL to clear all bodies.
    S to save current system.
    L to load system in `save.data`
    +/- or mouse wheel to adjust placed body mass
    R to toggle 1/r^2 and 1/r gravity. 1/r default, as it tends to be more fun.

## Images
| Falling in | Chaotic system |
| -- | -- |
| ![](https://i.imgur.com/jo1hytY.png) | ![](https://i.imgur.com/KLnWurh.png) |

## Gravity modes
By default, we use an unphysical 1/r scaling of gravity instead of 1/r^2. You can toggle this by pressing 'R'. The reason for this is that the simulation tends to create more interesting patterns and act less pathologically under inverse linear gravity. Under 1/r^2, your system either consists of stable orbits, or catapults itself into oblivion.

| Drifting together |
| -- |
| ![](https://i.imgur.com/4kBS9wa.png) |