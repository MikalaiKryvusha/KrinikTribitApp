"""Turn a wired phone into another screen over adb: size, density, orientation - and back.

Layout checks need many screens; the owner gave one phone on a cable (Samsung A51) and the word: "настраиваешь по ADB
его в режим другого девайса, разрешение, плотность пикселей, ориентация" (chat 2026-10-16 ~08:40 +03:00).

Usage (any shell; adb is taken from the SDK, not from PATH - see HOUSE_RULES.md section 3):
    python tools/screen_profile.py list
    python tools/screen_profile.py show                         [--serial R58N615KXZZ]
    python tools/screen_profile.py apply titan --land           # a profile + orientation
    python tools/screen_profile.py apply custom --size 900x1600 --density 280 --port
    python tools/screen_profile.py reset                        # native size, density and the saved rotation

The first `apply` saves the device's own rotation mode into out/screen-profile-<serial>.json (out/ is ignored);
`reset` restores it, so the owner's auto-rotate survives any number of profiles.
[TESTED: 2026-10-16 · A51: two cycles titan --land -> small --port -> reset, device read back native size/density and
auto-rotate "free" 5 s later; login screen shot in 6 profiles · testcases/reports/2026-10-16_a51_stand.md]
"""
import argparse
import json
import pathlib
import subprocess
import sys
import time

ADB = r"C:\Android\Sdk\platform-tools\adb.exe"
DEFAULT_SERIAL = "R58N615KXZZ"  # Samsung A51 on the cable
STATE_DIR = pathlib.Path(__file__).resolve().parent.parent / "out"

# name -> (width px, height px, density dpi, what it stands for). dp = px * 160 / dpi.
PROFILES = {
    "titan":  (1600, 2560, 480, "HEADWOLF Titan 1 at the owner's 480 dpi scale: 533x853 dp"),
    "design": (750, 1334, 320, "their design canvas 375x667 dp (AutoSize base of patch 11)"),
    "small":  (720, 1280, 320, "small phone 360x640 dp"),
    "tab7":   (1200, 1920, 320, "7-inch tablet 600x960 dp"),
}
# Rotation goes through WindowManager (`wm user-rotation`), never through `settings put system ...rotation`: WM keeps
# the mode in memory and writes it back over the settings after a size change (observed on the A51, Android 13: a
# restored auto-rotate=1 read back as 0 a moment later). `wm user-rotation` prints "free N" or "lock N" and takes the same.


def adb(serial, *args):
    """Runs one adb shell command on the device and returns its stdout without the trailing CR/LF."""
    out = subprocess.run([ADB, "-s", serial, "shell", *args], capture_output=True, text=True, check=True).stdout
    return out.strip()


def rotation(serial):
    """The rotation mode as WM holds it: 'free 3' (auto-rotate on) or 'lock 0' (locked portrait)."""
    return adb(serial, "wm", "user-rotation")


def state_file(serial):
    return STATE_DIR / f"screen-profile-{serial.replace(':', '_')}.json"


def save_rotation_once(serial):
    """Keeps the device's own rotation mode from before the first profile; later applies never overwrite it."""
    path = state_file(serial)
    if path.exists():
        return
    STATE_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps({"user_rotation": rotation(serial)}, indent=2), encoding="utf-8")


def set_orientation(serial, landscape):
    """Locks the rotation: landscape (1) or portrait (0)."""
    adb(serial, "wm", "user-rotation", "lock", "1" if landscape else "0")


def show(serial):
    """Prints what the device reports now - the observation, not what we asked for."""
    size = adb(serial, "wm", "size").replace("\n", " · ")
    density = adb(serial, "wm", "density").replace("\n", " · ")
    print(f"{serial}: {size} | {density} | rotation {rotation(serial)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=["list", "show", "apply", "reset"])
    parser.add_argument("profile", nargs="?", help="a name from `list`, or `custom` with --size and --density")
    parser.add_argument("--serial", default=DEFAULT_SERIAL)
    parser.add_argument("--size", help="WxH in px, for `custom`")
    parser.add_argument("--density", type=int, help="dpi, for `custom`")
    orient = parser.add_mutually_exclusive_group()
    orient.add_argument("--land", action="store_true", help="lock landscape")
    orient.add_argument("--port", action="store_true", help="lock portrait")
    args = parser.parse_args()

    if args.action == "list":
        for name, (w, h, dpi, note) in PROFILES.items():
            print(f"{name:7} {w}x{h} @ {dpi} dpi - {note}")
        return 0

    if args.action == "apply":
        if args.profile == "custom":
            if not (args.size and args.density):
                parser.error("custom needs --size WxH and --density N")
            size, density = args.size, args.density
        elif args.profile in PROFILES:
            w, h, density, _ = PROFILES[args.profile]
            size = f"{w}x{h}"
        else:
            parser.error(f"unknown profile {args.profile!r}; see `list`")
        save_rotation_once(args.serial)
        adb(args.serial, "wm", "size", size)
        adb(args.serial, "wm", "density", str(density))
        if args.land or args.port:
            set_orientation(args.serial, args.land)

    if args.action == "reset":
        adb(args.serial, "wm", "size", "reset")
        adb(args.serial, "wm", "density", "reset")
        path = state_file(args.serial)
        if path.exists():
            saved = json.loads(path.read_text(encoding="utf-8"))["user_rotation"]
            adb(args.serial, "wm", "user-rotation", *saved.split())
            time.sleep(2)  # WM settles after the size reset; read the mode after it, not before
            now = rotation(args.serial)
            if now.split()[0] != saved.split()[0]:
                print(f"WARNING rotation mode not restored: saved {saved!r}, device {now!r}; state kept in {path}")
                show(args.serial)
                return 1
            path.unlink()

    show(args.serial)
    return 0


if __name__ == "__main__":
    sys.exit(main())
