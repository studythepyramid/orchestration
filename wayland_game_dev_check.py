#!/usr/bin/env python3
"""Check an Ubuntu Wayland desktop for game development basics."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass


ENV_KEYS = [
    "XDG_SESSION_TYPE",
    "WAYLAND_DISPLAY",
    "DISPLAY",
    "XDG_CURRENT_DESKTOP",
    "DESKTOP_SESSION",
    "XDG_SESSION_DESKTOP",
    "XDG_SESSION_ID",
    "GDK_BACKEND",
    "QT_QPA_PLATFORM",
    "SDL_VIDEODRIVER",
    "GLFW_PLATFORM",
    "VK_ICD_FILENAMES",
    "__GLX_VENDOR_LIBRARY_NAME",
    "GBM_BACKEND",
    "STEAM_RUNTIME",
]

BASELINE_APT_PACKAGES = [
    "build-essential",
    "pkg-config",
    "git",
    "pciutils",
    "ripgrep",
    "cmake",
    "ninja-build",
    "meson",
    "vulkan-tools",
    "mesa-utils",
    "mesa-utils-extra",
    "wayland-utils",
    "libsdl2-dev",
    "libwayland-dev",
    "libxkbcommon-dev",
    "libvulkan-dev",
]

COMMAND_PACKAGES = {
    "gcc": "build-essential",
    "g++": "build-essential",
    "pkg-config": "pkg-config",
    "git": "git",
    "cmake": "cmake",
    "ninja": "ninja-build",
    "meson": "meson",
    "vulkaninfo": "vulkan-tools",
    "glxinfo": "mesa-utils",
    "eglinfo": "mesa-utils-extra",
    "wayland-info": "wayland-utils",
    "lspci": "pciutils",
    "nvidia-smi": "nvidia-utils",
    "steam": "steam-installer",
    "godot4": "godot",
    "godot": "godot",
    "blender": "blender",
    "cargo": "rustup or cargo",
}

WAYLAND_PROTOCOL_HINTS = {
    "xdg_wm_base": "modern toplevel windows",
    "zwp_relative_pointer_manager_v1": "relative mouse input",
    "zwp_pointer_constraints_v1": "pointer lock",
    "wp_fractional_scale_manager_v1": "fractional scaling",
    "wp_tearing_control_manager_v1": "tearing control",
    "wp_presentation": "frame presentation timing",
    "wp_linux_drm_syncobj_manager_v1": "explicit GPU sync",
}


@dataclass
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class Probe:
    name: str
    status: str
    detail: str
    action: str = ""


def run_command(args: list[str], timeout: float = 4.0) -> CommandResult:
    """Run a diagnostic command without invoking a shell."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
        return CommandResult(
            args=args,
            returncode=result.returncode,
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
        )
    except FileNotFoundError:
        return CommandResult(args=args, returncode=127, stdout="", stderr="")
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            args=args,
            returncode=124,
            stdout=(exc.stdout or "").strip()
            if isinstance(exc.stdout, str)
            else "",
            stderr="Command timed out.",
        )


def command_path(name: str) -> str | None:
    return shutil.which(name)


def first_present(names: list[str]) -> tuple[str, str] | None:
    for name in names:
        path = command_path(name)
        if path:
            return name, path
    return None


def package_hint(packages: list[str]) -> str:
    unique = []
    for package in packages:
        if package not in unique:
            unique.append(package)
    return "sudo apt install " + " ".join(unique)


def add_session_probes(probes: list[Probe], env: dict[str, str]) -> None:
    session_type = env.get("XDG_SESSION_TYPE", "").lower()
    if session_type == "wayland":
        probes.append(
            Probe(
                "Session type",
                "OK",
                "XDG_SESSION_TYPE=wayland.",
            )
        )
    elif session_type == "x11":
        probes.append(
            Probe(
                "Session type",
                "WARN",
                "The current login session is X11, not Wayland.",
                "Log out and choose an Ubuntu/GNOME Wayland session.",
            )
        )
    else:
        probes.append(
            Probe(
                "Session type",
                "INFO",
                "No desktop session was detected in this process.",
                "Run this script from a terminal inside the desktop.",
            )
        )

    if env.get("WAYLAND_DISPLAY"):
        probes.append(
            Probe(
                "Wayland display",
                "OK",
                f"WAYLAND_DISPLAY={env['WAYLAND_DISPLAY']}.",
            )
        )
    else:
        probes.append(
            Probe(
                "Wayland display",
                "INFO",
                "WAYLAND_DISPLAY is not set.",
                "Native Wayland clients need a Wayland socket.",
            )
        )

    if env.get("DISPLAY"):
        probes.append(
            Probe(
                "Xwayland fallback",
                "OK",
                f"DISPLAY={env['DISPLAY']} is available for X11 games.",
            )
        )
    else:
        probes.append(
            Probe(
                "Xwayland fallback",
                "INFO",
                "DISPLAY is not set.",
                "Many engines still use Xwayland on Linux.",
            )
        )


def add_tool_probes(probes: list[Probe]) -> None:
    required = [
        "gcc",
        "g++",
        "pkg-config",
        "git",
        "cmake",
        "ninja",
        "meson",
    ]
    missing_required = [name for name in required if not command_path(name)]
    if missing_required:
        packages = [COMMAND_PACKAGES[name] for name in missing_required]
        probes.append(
            Probe(
                "Native build tools",
                "WARN",
                "Missing: " + ", ".join(missing_required) + ".",
                package_hint(packages),
            )
        )
    else:
        probes.append(
            Probe(
                "Native build tools",
                "OK",
                "gcc, g++, pkg-config, git, cmake, ninja, and meson found.",
            )
        )

    for name in ["vulkaninfo", "glxinfo", "eglinfo", "wayland-info"]:
        path = command_path(name)
        if path:
            probes.append(Probe(name, "OK", f"Found at {path}."))
        else:
            probes.append(
                Probe(
                    name,
                    "WARN",
                    "Command not found.",
                    f"Install package: {COMMAND_PACKAGES[name]}.",
                )
            )

    engine = first_present(["godot4", "godot"])
    if engine:
        probes.append(
            Probe(
                "Godot editor",
                "OK",
                f"Found {engine[0]} at {engine[1]}.",
            )
        )
    else:
        probes.append(
            Probe(
                "Godot editor",
                "INFO",
                "Godot was not found on PATH.",
                "Install Godot from the official build, Steam, or Flatpak.",
            )
        )

    for name in ["steam", "blender", "cargo"]:
        path = command_path(name)
        status = "OK" if path else "INFO"
        detail = f"Found at {path}." if path else "Command not found."
        action = ""
        if not path and name == "steam":
            action = "For Steam/Proton testing, install steam-installer."
        if not path and name == "cargo":
            action = "For Rust game tooling, install rustup."
        probes.append(Probe(name, status, detail, action))


def pkg_config_exists(module: str) -> bool:
    if not command_path("pkg-config"):
        return False
    result = run_command(["pkg-config", "--exists", module], timeout=2.0)
    return result.returncode == 0


def add_dev_library_probes(probes: list[Probe]) -> None:
    modules = {
        "sdl2": "libsdl2-dev",
        "wayland-client": "libwayland-dev",
        "xkbcommon": "libxkbcommon-dev",
        "vulkan": "libvulkan-dev",
    }
    missing = [name for name in modules if not pkg_config_exists(name)]
    if missing:
        packages = [modules[name] for name in missing]
        probes.append(
            Probe(
                "Native dev libraries",
                "WARN",
                "Missing pkg-config modules: " + ", ".join(missing) + ".",
                package_hint(packages),
            )
        )
    else:
        probes.append(
            Probe(
                "Native dev libraries",
                "OK",
                "SDL2, Wayland, xkbcommon, and Vulkan dev files found.",
            )
        )


def summarize_lspci(text: str) -> str:
    blocks: list[list[str]] = []
    current: list[str] = []
    header_re = re.compile(r"\b(VGA|3D|Display)\b", re.IGNORECASE)
    for line in text.splitlines():
        if line and not line.startswith(("\t", " ")):
            if current:
                blocks.append(current)
                current = []
            if header_re.search(line):
                current = [line.strip()]
        elif current and (
            "Kernel driver in use" in line or "Kernel modules" in line
        ):
            current.append(line.strip())
    if current:
        blocks.append(current)
    if not blocks:
        return "No VGA/3D/Display PCI devices were found."
    return " | ".join(" ; ".join(block) for block in blocks)


def interesting_lines(text: str, patterns: list[str], limit: int = 8) -> str:
    found: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(pattern in stripped for pattern in patterns):
            found.append(stripped)
        if len(found) >= limit:
            break
    return "; ".join(found)


def summarize_wayland_info(text: str) -> str:
    found = [
        f"{name} ({meaning})"
        for name, meaning in WAYLAND_PROTOCOL_HINTS.items()
        if name in text
    ]
    if not found:
        return "No known game-related Wayland protocols were detected."
    return "; ".join(found)


def add_runtime_probes(probes: list[Probe]) -> None:
    if command_path("lspci"):
        result = run_command(["lspci", "-nnk"], timeout=4.0)
        detail = summarize_lspci(result.stdout)
        probes.append(Probe("GPU PCI devices", "INFO", detail))

    if command_path("nvidia-smi"):
        result = run_command(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ],
            timeout=4.0,
        )
        status = "OK" if result.returncode == 0 else "WARN"
        detail = result.stdout or result.stderr or "nvidia-smi failed."
        probes.append(Probe("NVIDIA driver", status, detail))

    if command_path("vulkaninfo"):
        result = run_command(["vulkaninfo", "--summary"], timeout=6.0)
        detail = interesting_lines(
            result.stdout,
            [
                "Vulkan Instance Version",
                "deviceName",
                "driverName",
                "driverInfo",
                "apiVersion",
            ],
        )
        status = "OK" if result.returncode == 0 and detail else "WARN"
        action = ""
        if status == "WARN":
            detail = result.stderr or result.stdout or "vulkaninfo failed."
            action = "Check GPU drivers and Vulkan ICD packages."
        probes.append(Probe("Vulkan runtime", status, detail, action))

    if command_path("glxinfo"):
        result = run_command(["glxinfo", "-B"], timeout=4.0)
        detail = interesting_lines(
            result.stdout,
            [
                "OpenGL vendor string",
                "OpenGL renderer string",
                "OpenGL core profile version string",
            ],
        )
        status = "OK" if result.returncode == 0 and detail else "INFO"
        if not detail:
            detail = result.stderr or result.stdout or "glxinfo failed."
        probes.append(Probe("OpenGL/Xwayland runtime", status, detail))

    if command_path("wayland-info"):
        result = run_command(["wayland-info"], timeout=4.0)
        status = "OK" if result.returncode == 0 else "INFO"
        detail = summarize_wayland_info(result.stdout)
        if result.returncode != 0:
            detail = result.stderr or "wayland-info could not connect."
        probes.append(Probe("Wayland protocols", status, detail))


def collect_environment() -> dict[str, str]:
    return {key: os.environ.get(key, "") for key in ENV_KEYS}


def build_report(run_probes: bool) -> dict[str, object]:
    env = collect_environment()
    probes: list[Probe] = []
    add_session_probes(probes, env)
    add_tool_probes(probes)
    add_dev_library_probes(probes)
    if run_probes:
        add_runtime_probes(probes)

    recommendations = [
        "Baseline apt packages: "
        + package_hint(BASELINE_APT_PACKAGES),
        "Prefer Vulkan for new Linux render paths; keep OpenGL tested.",
        "Set SDL_VIDEODRIVER=wayland per run only when testing native "
        "Wayland. Use SDL_VIDEODRIVER=x11 to compare Xwayland.",
        "Do not export game backend variables globally in shell startup "
        "files; engine launchers and tools may need different backends.",
    ]
    return {
        "environment": env,
        "probes": [asdict(probe) for probe in probes],
        "recommendations": recommendations,
    }


def print_report(report: dict[str, object]) -> None:
    print("Ubuntu Wayland game development check")
    print("=" * 43)
    print()
    print("Environment")
    print("-----------")
    environment = report["environment"]
    assert isinstance(environment, dict)
    for key in ENV_KEYS:
        value = environment.get(key) or "(unset)"
        print(f"{key}={value}")

    print()
    print("Checks")
    print("------")
    probes = report["probes"]
    assert isinstance(probes, list)
    for probe in probes:
        status = probe["status"]
        name = probe["name"]
        detail = probe["detail"]
        action = probe.get("action", "")
        print(f"[{status}] {name}: {detail}")
        if action:
            print(f"       Next: {action}")

    print()
    print("Recommendations")
    print("---------------")
    recommendations = report["recommendations"]
    assert isinstance(recommendations, list)
    for item in recommendations:
        print(f"- {item}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a desktop for Ubuntu Wayland game development."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the report as JSON",
    )
    parser.add_argument(
        "--no-probe",
        action="store_true",
        help="skip runtime commands and inspect environment/PATH only",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when any check has WARN status",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(run_probes=not args.no_probe)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_report(report)

    if args.strict:
        probes = report["probes"]
        assert isinstance(probes, list)
        if any(probe["status"] == "WARN" for probe in probes):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
