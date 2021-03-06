# n-body-pygame
N-body simulation in pygame. Supports saving/loading, custom colours, click-drag to shoot, right click to remove masses. Save your own preferences in `settings.json`. Consider lowering trail_length for better performance. `sim_precision` increases numerical accuracy somewhat, but isn't that important in general. It's actually also the framerate, so keep it at least at your monitor's value (blame pygame for this).

![](https://i.imgur.com/WWlqsLq.png)
## Controls

    Left click and drag to shoot a body in a direction. Just click for no initial velocity.
    Mouse wheel or +/- to adjust placed body mass.
    SPACE to pause and unpause.
    Right click on a body to delete it.
    F to toggle camera centering.
    DEL to clear all bodies.
    S to save current system.
    L to load system in `save.data`
    R to toggle 1/r^2 and 1/r gravity.

## Images
| Falling in |
| -- |
| ![](https://i.imgur.com/RDpkToI.png) | 
| Drifting together |
| ![](https://i.imgur.com/XLuPwZI.png) |
| Orbits around a binary system |
| ![](https://i.imgur.com/AgzjSTa.png) |
| Another binary pair |
| ![](https://i.imgur.com/m56KxiO.png) |

## Gravity modes
By default, we use realistic 1/r^2 gravity, but a 1/r option is included. You can toggle this by pressing 'R'. The reason for this is that the simulation tends to create more interesting (stable), though unphysical patterns under 1/r gravity.

|  Chaotic 1/r system|
| -- |
| ![](https://i.imgur.com/T6i7JOR.png) |