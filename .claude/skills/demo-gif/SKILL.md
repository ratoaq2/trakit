---
name: demo-gif
description: Record the README terminal demo docs/images/demo.gif with VHS in a container. Use to make or update the demo GIF.
---

# Demo GIF

`docs/images/demo.gif` shows a trakit session in a terminal. VHS records it in a container:

- `scripts/demo.tape`: the session that VHS types and records. It is the source of the current GIF.
- `scripts/demo.Dockerfile`: Python, trakit from this repository, VHS, ttyd, and Chromium.
- `scripts/demo.sh`: builds the image, mounts the repository on `/repo`, and records.

trakit reads only strings. The tape needs no file.

## 1. Edit the tape

Change only the lines that you must change: the `trakit` commands.

- Keep the hidden setup at the top. It goes to `/tmp` and sets the prompt to `$ `. The GIF must not show
  a path of the host. A shell function removes the version from the `trakit <version> found:` line, so
  that the GIF does not show a dev version and does not change at each release.
- Keep the `Wait+Line` before `Show`. Without the wait, the first frames show the hidden command.
- All the output must fit on one screen. If it does not, change `Set Height` and `Set FontSize`. Do not
  let the output scroll.

## 2. Record

1. On Windows or macOS, start the Podman machine: `podman machine start`. It is not an error if it runs
   already.
2. From the repository root, run `bash scripts/demo.sh`. The first build takes some minutes. The next runs
   take about 1 minute.
3. The output ends with `Creating docs/images/demo.gif...`. If it ends with `recording failed`, read the
   last value that VHS shows.

Known problems that the scripts already solve:

- Debian has no `ttyd` package. `scripts/demo.Dockerfile` downloads the static binary.
- Git Bash changes `/repo` into a Windows path. `scripts/demo.sh` sets `MSYS_NO_PATHCONV=1`.
- Podman on WSL fails with "controller `pids` is not available". `scripts/demo.sh` adds
  `--cgroups=disabled` for Podman.
- `Wait+Screen` reads the screen from the top. The tape waits for the `$ ` prompt line with `Wait+Line`.
- VHS does not accept `\"` in a string. A string in backticks can have both `"` and `'`. If VHS shows
  `parser: N error(s)`, it does not record, and the old `docs/images/demo.gif` stays.

## 3. Check the frames

Save some frames as PNG, then read them:

```
uv run --no-project --with pillow python -c "
from PIL import Image
im = Image.open('docs/images/demo.gif')
n = im.n_frames
print(im.size, n, 'frames', sum((im.seek(i), im.info.get('duration', 0))[1] for i in range(n)) / 1000, 's')
for k, f in enumerate(range(0, n, n // 6)):
    im.seek(f)
    im.convert('RGB').save(f'plans/demo-gif/frame{k}.png')
"
```

Look for these problems:

- The last screen is too short to read: increase the last `Sleep`.
- A path of the host, or a command of the hidden setup, is in a frame.
- The GIF is more than about 2 MB or 20 s.

Record again after each change. Delete the PNG files when you are done.

## 4. Finish

1. Show some frames to the user, with the size and the duration of the GIF.
2. `README.md` shows `docs/images/demo.gif` with an absolute `raw.githubusercontent.com` URL, so that PyPI
   shows it too. Change its alt text if the content changed.
3. Commit `docs/images/demo.gif` and `scripts/demo.tape` together, after the user reviews them.
