# Lab 7 Start and trace-download investigation

The owner reported tapping **Start** in Lab 7, “Muscle under skin and elbow contact,” and receiving `kenoma-spatial-trace.json`. The same problem persisted in external Android Chrome after first appearing in the ChatGPT Android browser. This filename identifies the spatial trace export handler; it does not establish which DOM element received the owner's touch or why the interactive remained blank.

This follow-up preserves the separate mobile startup repair candidate at `81bcd55e7c2a9c7dd3f11bd5206dd96c807a8bd4` (PR 5). It adds bounded local interaction diagnostics and a stronger touch contract without changing mechanics, anatomy data, book content, or Lean claims.

## Evidence and limits

Locally served artifacts of the deployed main source tree and PR 5 were tested with default headless Chromium and native Playwright touchscreen input. The deployed main head was `955dc6ec9b56d0afe4b6d1084bffec78644ca2a2`; its tree matches the earlier checked `c2f271e` artifact. The normal-layout matrix covered both artifacts at 320, 360, 375, 393, and 412 CSS pixels, with normal and reduced motion: 20 cases. Nine points inside each Start hitbox resolved to Start. The original center touch still targeted Start at 0, 50, 150, and 400 milliseconds after initialization. Repeated center taps downloaded nothing.

A separate 12-case fault matrix covered both artifacts at 320, 360, and 412 pixels with injected unavailable WebGL, both at default root font size and an explicit 24-pixel CSS font stress setting. The original touch still targeted Start and downloaded nothing. These are controlled faults and font stress tests, not observations of the owner's settings or browser capability.

The repository mobile suite additionally makes 45 native Start taps across the five widths, at nine fractional positions within the button. Every tap must resolve to Start, reach a ready scene, and produce no download. A separate intentional native tap on Download trace must resolve to export and download exactly `kenoma-spatial-trace.json`. Its exported diagnostics must record trusted pointerdown, pointerup, and click events for export, with preceding trusted Start events.

Neither the normal matrix nor the fault matrix reproduced the owner's unintended download. These checks use mobile emulation on a software renderer, not physical Android or ChatGPT WebView evidence. Public-site requests from the execution environment are proxy-blocked; no browser, network, or security policy was relaxed to bypass that restriction. The actual owner-device event sequence and blank-scene cause remain unresolved.

## Local diagnostics

The spatial export envelope now includes `interactionDiagnostics`, separate from its numerical `trace`. Each laboratory retains only its last 32 button pointerdown, pointerup, and click events in memory. Entries record the button action and label, trusted-event flag, CSS touch coordinate and contact size, button rectangle, scroll position, layout/visual viewport geometry, scene state, and wall-clock milliseconds. Wall-clock time is not simulation time. No typed input values are collected; no diagnostics are transmitted automatically. Refreshing clears the in-memory history.

Visible 3D failure details also include this bounded local history, allowing the actual scene error to be read alongside the recent button targets. Diagnostic metadata does not validate the biomechanical model, floating-point solver, or phone hardware. An owner-device export or visible failure details from this follow-up would distinguish a Start-handler failure from an export touch after a layout change.
