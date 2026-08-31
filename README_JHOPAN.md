# Grok Register - TempMail Edition

Fork dari [AaronL725/grok-register](https://github.com/AaronL725/grok-register) dengan integrasi TempMail By JhopanStore.

## Perubahan Utama

1. **Email Provider** - Hanya menggunakan TempMail By JhopanStore (self-hosted)
2. **Blocking Wait** - Tidak ada polling loop, lebih efisien
3. **Server-side Extraction** - Verification codes dan links di-extract otomatis

## Quick Start

```bash
# Clone
git clone https://github.com/jhopan/grok-register.git
cd grok-register

# Setup venv
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install
pip install -r requirements.txt

# Config
copy config.example.json config.json
# Edit config.json - isi tempmail_api_key

# Run
python grok_register_ttk.py
```

## Configuration

Edit `config.json`:

```json
{
  "tempmail_api_base": "https://renunganbot.qzz.io",
  "tempmail_api_key": "your-api-key-here",
  "tempmail_domain": "renunganbot.qzz.io",
  "register_count": 1
}
```

API Key: lihat `/etc/tempmail/tempmail.env` di server TempMail.

## Documentation

- [Full Integration Docs](TEMPMAIL_INTEGRATION.md)
- [Original README](README.md)

## Requirements

- Python 3.9+
- Chrome/Chromium
- TempMail By JhopanStore (running)

## License

MIT (sama seperti upstream)
