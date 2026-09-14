# 📸 Face_recognition — deploy notes !

A little attendance system that watches faces and asks where you are (っ˘ω˘ς ) YuNet finds the face, SFace says who it is, the browser tattles on your GPS. Lives on a Proxmox CT, talks HTTPS because browsers throw a fit about camera access otherwise.

## The gotcha ⚠️⋆｡°✩

`.gitignore` has this line:

```
database/
```

Looked innocent, meant to ignore the `.db` file, actually swallowed the **entire folder**, including `database/database.py`, which is real source code the app imports. So is `dataset/`, `models/`, and `cert/`. None of these ever made it to GitHub. Clone the repo fresh and it will NOT run out of the box, and that's not a deploy mistake, that's just what's in the repo (´-ω-`)

## What actually needs to be hand-carried per deploy ᶻ 𝗓 𐰁

```
face-recognition/
├── database/
│   ├── database.py      ← MISSING FROM REPO. get from a working copy or a teammate ( ๑❛▿❛)( *’▿’)
│   └── database.db      ← MISSING FROM REPO. has real accounts + attendance history in it (╭ರ_•́)
├── dataset/              ← MISSING FROM REPO. face photos per person, scp -r the whole folder 
├── models/
│   ├── detector/*.onnx   ← missing but not precious, just re-download (see below)( ദ്ദി ˙ᗜ˙ )
│   ├── recognizer/*.onnx ← same, re-downloadable 
│   └── embeddings/
│       └── embeddings.pkl  ← don't copy this one, REBUILD it after dataset/ lands (see Training) ( •̀ ᴖ •́ )
└── cert/
    ├── server.crt        ← regenerate fresh every deploy, needs THIS server's IP in it 
    └── server.key
```

## Models ; safe to just grab fresh ⋆.˚

These are OpenCV's own public zoo models, nothing custom-trained, no need to hunt them down from anyone:

```bash
mkdir -p models/detector models/recognizer
cd models/detector && wget https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
cd ../recognizer && wget https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx
```

Detector should land ~230KB, recognizer ~37MB. If it's way smaller, the download broke, try again.

## Cert ; bind it to whatever IP will actually be typed in 

Self-signed, IP-based (no domain for this one). Needs BOTH the internal CT IP and the public NAT IP in the SAN, or Chrome/WebView just flatly rejects it instead of showing the click-through warning:

```bash
cd cert
openssl req -x509 -nodes -newkey rsa:2048 -keyout server.key -out server.crt -days 825 \
  -subj "/CN=<public-ip>" \
  -addext "subjectAltName=IP:<public-ip>,IP:<internal-ct-ip>"
```

## Shared folders ; symlink, don't nest 🔗

The app wants `database/`, `dataset/`, `attendance_images/`, `models/`, `cert/` right next to `app.py`. Keep the real data in a `shared/` folder outside the code, symlink it in — that way redeploying the code later doesn't wipe anyone's face data:

```bash
ln -s shared/database database
ln -s shared/dataset dataset
ln -s shared/attendance_images attendance_images
ln -s shared/models models
ln -s shared/cert cert
```

## Training ; do this AFTER dataset/ lands, every single time ♪

Registering a person in the DB ≠ the recognizer knowing their face. `embeddings.pkl` has to be generated (or regenerated) from whatever's sitting in `dataset/`:

```bash
systemctl stop face-recognition   # don't let two processes touch it at once
source venv/bin/activate
python3 -c "from training.train import train_all; train_all()"
systemctl start face-recognition
```

Forget this step and everyone gets "Wajah tidak dikenali" forever, looking very confused at the camera for no reason (˶˃𐃷˂˶)

## Running it ; plain Flask, not gunicorn, on purpose 🎈

The app has in-memory global state (camera manager, liveness sessions) and wires its own `ssl_context` straight into `app.run()`. Multi-worker WSGI servers would split that state across processes and lose the SSL config entirely. Just run it directly under systemd:

```ini
[Unit]
Description=Face Recognition Attendance System
After=network.target

[Service]
Type=simple
WorkingDirectory=/var/www/face-recognition
ExecStart=/var/www/face-recognition/venv/bin/python3 /var/www/face-recognition/app.py
Restart=on-failure
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

⚠️ Double check whether your venv folder is named `venv` or `.venv` before pasting the `ExecStart` path — mismatching this is a `203/EXEC` error that gives you basically zero hints why.

## Don't forget the boring server stuff, it bites (°⌓°;)

- **Timezone**: fresh Debian CTs default to UTC. Attendance timestamps will be quietly wrong (off by 7 hrs from WIB) until you run:
  ```bash
  timedatectl set-timezone Asia/Jakarta
  ```
  then `systemctl restart face-recognition` — the running process caches the old tz otherwise, changing system time alone isn't enough.
- **SSH root login**: fresh CTs often block root password auth by default. If ssh just says "Permission denied" with a correct password, check `/etc/ssh/sshd_config` for `PermitRootLogin` / `PasswordAuthentication` and add them explicitly if missing.
- **NAT rule**: needs an explicit `dst-address` on the MikroTik rule or it'll misroute. Browsers default to `http://` when no scheme is typed, and this app is HTTPS-only, so always share the full `https://...` link, not just the bare IP:port.

## tl;dr checklist for next time ⊹₊⟡⋆

- [ ] clone repo
- [ ] get `database/database.py` from a working copy
- [ ] get `database/database.db` from whoever has the real one, or start empty on purpose
- [ ] `scp -r dataset/` over
- [ ] download detector + recognizer `.onnx` fresh
- [ ] generate cert with correct IPs in SAN
- [ ] symlink shared folders in
- [ ] run `train_all()` — every time dataset changes, not just once
- [ ] set timezone, restart service
- [ ] systemd service running, `venv` path double-checked
- [ ] NAT rule has explicit dst-address
- [ ] tell people the full `https://` link, not just the IP