# Purpose

**Problem:** 3D printing knowledge is scattered and perishable — a model lives in one place, the slicer settings that made it print cleanly live in the slicer, and the reason a print failed lives only in memory. Reprinting an object months later means rediscovering all of it.

**Audience:** Jerry, and anyone who wants to reprint one of these objects successfully on the first attempt.

**Key constraints:** Source geometry is versioned, not just exported meshes; every project records the settings it was actually printed with; slicer profiles are stored per printer so they stay reproducible; generators stay in `openSCAD` and `stencils` rather than being duplicated here.

**Success metric:** Any project in this repo can be reprinted from a cold start — pick the folder, load the named profile, print — with no guesswork about orientation, supports, or material.
