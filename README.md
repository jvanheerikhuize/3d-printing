# 3D Printing

Print-ready projects, slicer profiles, and build notes for physical objects. This is the home for finished and in-progress 3D printing work — the models themselves, the settings that made them print well, and what was learned along the way.

## Layout

```
models/     Per-project directories: source geometry, exported STLs, photos, notes
profiles/   Slicer profiles and filament settings, grouped by printer
prints/     Print logs — what was printed, with which settings, and how it came out
```

## Quick start

1. Pick a project under [`models/`](models/) and read its `README.md` for print orientation, supports, and material.
2. Load the matching profile from [`profiles/`](profiles/) into your slicer.
3. Slice, print, and record the result in [`prints/`](prints/).

## Adding a project

Create `models/<project-name>/` with:

- `README.md` — what it is, print settings, assembly notes
- source geometry (`.scad`, `.f3d`, `.svg`, …) — committed
- exported meshes (`.stl`, `.3mf`) — see [.gitignore](.gitignore); commit release exports deliberately with `git add -f`

## Related repos

- **[openSCAD](../openSCAD/)** — parametric generators that *produce* printable geometry
- **[stencils](../stencils/)** — SVG-to-stencil pipeline and generated stencil files

This repo holds the projects and print knowledge; those two hold the generators that feed it.

## License

Licensed under the [MIT License](LICENSE).

## Roadmap

Seed with existing prints, establish a per-printer profile baseline, and standardize the per-project README format.

---
