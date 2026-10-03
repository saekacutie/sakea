# sakea — Termux Multi-Tool

A Termux toolkit by **prvtspyyy404**: a menu-driven collection of network and
device utilities with a styled terminal UI.

## Install (Termux)

```bash
chmod +x setup.sh
./setup.sh
# then type: saeka
```

`setup.sh` installs system packages, the Python requirements, downloads `main.py`,
and adds a `saeka` alias to `~/.bashrc`.

## Manual run

```bash
pip install -r requirements.txt
python3 main.py
```

## Files

| File | Purpose |
|---|---|
| `main.py` | The toolkit |
| `setup.sh` | Termux installer (adds `saeka` alias) |
| `requirements.txt` | Pinned Python dependencies |
| `config/settings.py` | Settings |

## Security notes

- Review the source before running — it performs network operations.
- Never paste credentials or one-time codes into tools you don't trust.
