# Mobile 3D startup investigation

Baseline: main `955dc6ec9b56d0afe4b6d1084bffec78644ca2a2`, tree
`d9bdf17d8fe8a898ab3f45092becd53aa362e7cc` (same source tree as the accepted
`c2f271e` candidate). The owner reports blank scenes after Start and a JSON
download, both in ChatGPT's Android browser and external Chrome. The exact
laboratory and downloaded filename remain needed to identify that symptom.

Confirmed separately:

- Pandoc emits two newlines inside every idle `.scene-host`. Therefore the
  `:empty` selector does not hide it: all seven numbered labs show a blank
  300-pixel area before initialization. The new idle-viewport assertion fails
  against the baseline artifact.
- The Start control is below the full parameter panel, 152–719 CSS pixels
  after that blank area in Pixel 7 emulation. Initialization errors are
  reported still farther down, outside the apparent viewport.
- The old renderer only catches constructor errors. Drawing/shader errors or
  a later WebGL context loss have no visible scene-level recovery path.
- Coordinate taps on the actual baseline Start buttons reach the correct
  handlers in all seven labs, download no files and draw nonblank geometry in
  this environment's default headless Chromium. The reported JSON download
  was **not reproduced**, and these observations do not establish the owner
  phone's renderer behavior.

The root's separate public-browser test reached Three.js initialization and
reported disabled GL vendor/renderer. That demonstrates that browser's
restriction, not an Android hardware diagnosis. This execution environment
could not reach the public Pages URL: its proxy returned
`ERR_TUNNEL_CONNECTION_FAILED`. Locally served, source-bound artifacts were
used here. No network, security, WebGL or browser-policy settings were changed.

## Bounded candidate

Start is a dedicated native button above the static figure, separate from
trace/export actions. Idle scene containers are explicitly hidden, independent
of whitespace. A shared scene-status helper exposes initializing, ready and
failed states. Constructor, drawing/shader and context-loss failures restore
the static alternative and show diagnostic details in the scene location;
Retry attempts the real renderer again. Numerical controls remain functional
and are clearly described as operating without 3D after a rendering failure.
No substitute renderer or simulated 3D screenshot is used.

Diagnostics stay on the page and browser console: laboratory, failure stage,
error reason, user agent, pixel ratio and actual last-observed GL context
properties. A successful initial scene requires real draw calls and a live
context. Book, mechanics algorithms, numerical parameter values, Lean sources
and anatomy/data bytes are unchanged.

`npm run test:mobile` uses Pixel 7 touch emulation and default Chromium with
**no GL or security override flags**. It checks actual coordinate hit targets,
repeated Start taps without downloads, and substantial colored geometry in
composited canvas screenshots for every lab plus the atlas. It also checks an
actual `WEBGL_lose_context` loss/retry, injected post-context drawing failure,
and explicitly injected unavailable WebGL in all seven labs. All three
failure cases require visible diagnostics; numerical fallback is tested
without claiming it is 3D. Artifact validation binds this receipt to the
current HTML/application hashes. Physical Android/WebView verification and
identification of the owner's JSON-download path remain pending.
