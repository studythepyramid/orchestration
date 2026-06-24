# Game Development on Ubuntu Wayland

This note is a practical checklist for building and testing games on an
Ubuntu desktop that uses Wayland. It focuses on the Linux desktop pieces
that often affect game engines: graphics drivers, Vulkan/OpenGL,
Xwayland fallback, input capture, display scaling, and packaging tools.

Run the local checker first:

```bash
python wayland_game_dev_check.py
```

For machine-readable output:

```bash
python wayland_game_dev_check.py --json
```

## Baseline packages

Install native build tools and the most useful desktop diagnostics:

```bash
sudo apt update
sudo apt install \
  build-essential pkg-config git pciutils ripgrep \
  cmake ninja-build meson \
  vulkan-tools mesa-utils mesa-utils-extra wayland-utils \
  libsdl2-dev libwayland-dev libxkbcommon-dev libvulkan-dev
```

Optional tools, depending on your stack:

```bash
sudo apt install steam-installer blender
```

For Rust game projects, prefer `rustup` from the Rust project over the
older distro `cargo` packages when you need current toolchains.

## Confirm the desktop session

Wayland-native testing needs a Wayland login session:

```bash
echo "$XDG_SESSION_TYPE"
echo "$WAYLAND_DISPLAY"
echo "$DISPLAY"
```

Expected values:

- `XDG_SESSION_TYPE=wayland`
- `WAYLAND_DISPLAY` is set, such as `wayland-0`
- `DISPLAY` is also often set for Xwayland compatibility

If the session is X11, log out and choose the Ubuntu or GNOME Wayland
session from the login screen. Some NVIDIA configurations or remote
desktop sessions may still choose X11 unless the driver and compositor
support Wayland well.

## Graphics driver checks

Use Vulkan as the primary render path for new Linux game work, then keep
OpenGL tested as a compatibility path.

```bash
vulkaninfo --summary
glxinfo -B
wayland-info
```

General driver notes:

- AMD and Intel usually use Mesa. Keep Mesa packages current from the
  Ubuntu release or a trusted graphics PPA only when you need it.
- NVIDIA usually needs the Ubuntu-recommended proprietary driver for the
  GPU generation. Prefer the current recommended driver from "Additional
  Drivers" or `ubuntu-drivers`.
- `glxinfo` reports the OpenGL path, commonly through Xwayland.
- `vulkaninfo` confirms that Vulkan ICD files and GPU drivers are
  visible to native applications.

## Native Wayland versus Xwayland

Many Linux games and editors still run through Xwayland. That is normal.
Treat Wayland-native and Xwayland as two test targets:

- Native Wayland: better compositor integration, modern scaling, and
  direct Wayland input/display protocols.
- Xwayland: necessary fallback for engines, launchers, overlays, and
  older middleware that still assume X11.

Do not export backend variables globally in `.bashrc` or `.profile`.
Set them per command so that each engine can choose the correct backend.

Examples:

```bash
SDL_VIDEODRIVER=wayland ./your_sdl_game
SDL_VIDEODRIVER=x11 ./your_sdl_game
GLFW_PLATFORM=wayland ./your_glfw_game
```

## Engine notes

### SDL

SDL is a good first target for Wayland experiments because the backend
can be selected per run:

```bash
SDL_VIDEODRIVER=wayland ./game
SDL_VIDEODRIVER=x11 ./game
```

If native Wayland has input capture or windowing issues, compare the same
build under Xwayland before changing game logic.

### GLFW

Modern GLFW can target Wayland when it was built with Wayland support.
Use:

```bash
GLFW_PLATFORM=wayland ./game
```

If a distro GLFW build lacks the Wayland platform, rebuild GLFW with
Wayland development headers installed.

### Godot

Godot is a good editor for fast iteration on Linux. Keep two launch
profiles while testing:

- the default editor/runtime path
- a forced native Wayland or forced Xwayland path when supported by the
  installed Godot build

Keep exported builds tested outside the editor, because editor behavior,
debug overlays, and packaged game behavior can differ.

### Unity and Unreal

Unity, Unreal, Steam, Proton, and many overlays commonly use Xwayland.
That is acceptable for shipping tests. For Linux support, always test:

- editor launch
- standalone build launch
- fullscreen and borderless modes
- gamepad and mouse capture
- Steam/Proton path if the game is distributed there

## Wayland-specific test cases

Create a small manual checklist for every game prototype:

- Windowed, borderless, and fullscreen modes
- Alt-tab and monitor focus changes
- Pointer lock and relative mouse movement
- Gamepad hotplug
- Fractional scaling, if enabled
- Multi-monitor placement
- Audio device changes
- Screen recording through PipeWire/portals
- Steam overlay or other overlays, if used
- Vulkan validation layers in debug builds

Wayland compositors control presentation more strictly than X11 window
managers. If frame pacing feels wrong, compare native Wayland, Xwayland,
fullscreen, and borderless modes before changing renderer timing code.

## Useful commands

```bash
# Desktop/session basics
echo "$XDG_SESSION_TYPE $XDG_CURRENT_DESKTOP"
loginctl show-session "$XDG_SESSION_ID" -p Type -p Desktop -p State

# GPU and drivers
lspci -nnk | rg -A3 'VGA|3D|Display'
vulkaninfo --summary
glxinfo -B

# Wayland protocol support
wayland-info | rg 'xdg_wm_base|relative_pointer|pointer_constraints'
wayland-info | rg 'fractional_scale|tearing_control|presentation'

# SDL library visibility for native builds
pkg-config --modversion sdl2
pkg-config --cflags --libs sdl2
```

## First prototype target

For a small Ubuntu Wayland game prototype, a conservative stack is:

- SDL2 for windows, input, and gamepads
- Vulkan for rendering, or OpenGL while learning
- CMake or Meson for native builds
- `vulkaninfo`, `glxinfo`, and `wayland-info` as the first diagnostics

This keeps the prototype close to the Linux desktop APIs without forcing
a large engine decision too early.
