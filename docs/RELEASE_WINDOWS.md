# Windows Packaging and Installer

This project can now produce:
- a portable `DJSelector.exe` app bundle via PyInstaller
- a Windows installer `.exe` via Inno Setup

## Local build (Windows)
1. Bootstrap environment:
   - `./scripts/dev-setup-windows.ps1`
2. Install Inno Setup 6.
3. Build package and installer:
   - `./scripts/build-windows-package.ps1 -Version 0.1.0`

Artifacts:
- Portable bundle: `dist/DJSelector/`
- Installer: `installer/windows/output/`

## CI build
Workflow: `.github/workflows/windows-release.yml`
- triggers on tags `v*` and manual `workflow_dispatch`
- uploads both portable and installer artifacts

## Notes
- This is unsigned output; for production distribution, add code signing.
- Audio device compatibility should still be validated on target hardware.
