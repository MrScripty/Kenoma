# Shared embedded presentation

`createViewport(container, options)` owns only Three.js camera, lighting,
orbit controls, rendering and GPU disposal. The simple poser and the book's
chapter adapters use this same component and `theme.css`. It imports neither
the research engine nor the poser model. An adapter owns its state and units.

Call `resize()` after layout changes, `frame(object)` to fit geometry, and
`render()` on demand or from an owned animation loop. `frame(object,
{preserveDirection:true})` refits changed geometry while retaining the orbit
direction; the chapter host uses it to keep edited models visible. Call `dispose()` exactly
when replacing/unmounting a view; it is idempotent. Do not retain its canvas or
GPU objects afterward. Creation may throw when WebGL is unavailable; the host
must retain its text/numerical alternative. The book loads one iframe at a time.

The theme matches the verified Rheon projection page's paper, ink, teal and
sage palette and editorial typography. It does not change physical models or
add sliders to the independent poser.
