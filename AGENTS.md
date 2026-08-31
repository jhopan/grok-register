# Grok Register - TempMail Edition

## Project Context

Automated registration tool for accounts.x.ai using TempMail By JhopanStore email service.

## Current Status

⚠️ **CRITICAL ISSUE: Email Domain Blacklist**

accounts.x.ai sekarang **memblacklist temporary email domains**:
- ❌ DuckMail domains (blocked)
- ❌ YYDS Mail domains (blocked)  
- ❌ Cloudflare public temp email domains (blocked)
- ❌ **renunganbot.qzz.io** - JUGA SUDAH DI-BLACKLIST!

**Root Cause:**
x.ai mendeteksi dan memblacklist semua temporary/disposable email domains yang terkenal.

## Solution Needed

Butuh **domain baru yang belum masuk blacklist** untuk TempMail:

1. **Register domain baru** (belum pernah dipakai untuk temp email)
2. Setup Cloudflare Email Routing untuk domain tersebut
3. Update TempMail config dengan domain baru
4. Forward email dari domain baru ke TempMail server

**Contoh domain yang bisa dicoba:**
- `inbox-verify.example.com` (subdomain dari domain legit)
- `mail.personal-domain.com` (terlihat seperti email personal)
- Hindari nama seperti: tempmail, disposable, temp, fake, etc

## Tech Stack

- **Backend:** Python 3.9+
- **Browser:** DrissionPage (Chromium automation)
- **Email:** TempMail By JhopanStore (self-hosted)
- **Server:** https://tempmail.renunganbot.qzz.io

## Architecture

```
Registration Flow:
1. Open accounts.x.ai/sign-up
2. Click "Sign up with email"
3. Create TempMail inbox (POST /api/inbox)
4. Submit email to x.ai
5. Wait for verification code (GET /api/inbox/{email}/wait)
6. Extract code from email
7. Submit code to x.ai
8. Fill profile
9. Get SSO cookie
10. Save account
```

## Files Structure

```
grok-register/
├── mail_service.py           # TempMail integration (256 lines)
├── app_config.py             # Config management
├── registration_browser.py   # Browser automation
├── registration_flow.py      # Registration orchestration
├── grok_register_ttk.py     # GUI/CLI entry point
├── config.json              # Active config (API key here)
├── test_real_api.py         # TempMail API test
└── accounts_*.txt           # Saved accounts
```

## Configuration

Edit `config.json`:

```json
{
  "tempmail_api_base": "https://tempmail.renunganbot.qzz.io",
  "tempmail_api_key": "e763e811971502063b94be13707b3d9990c921493a7234469293c73bc289176f",
  "tempmail_domain": "renunganbot.qzz.io",  // ← DOMAIN INI SUDAH DI-BLACKLIST!
  "register_count": 1,
  "proxy_mode": "auto"
}
```

## Known Issues

### 1. Email Domain Blacklisted ⚠️
**Symptom:** Email created successfully, but x.ai rejects it or never sends verification code.

**Cause:** x.ai maintains blacklist of temporary email domains.

**Solution:**
- Get new domain that's not blacklisted yet
- Setup Email Routing for new domain
- Update `tempmail_domain` in config.json
- Redeploy TempMail with new domain

### 2. Email Not Arriving
**Symptom:** Timeout waiting for code (HTTP 408).

**Causes:**
- Domain blacklisted (most likely)
- Cloudflare Email Routing not configured
- Email Worker not forwarding to TempMail server

**Debug:**
```bash
# Test inbox creation
curl -X POST https://tempmail.renunganbot.qzz.io/api/inbox \
  -H "Content-Type: application/json" \
  -H "X-Email-API-Key: e763e811971502063b94be13707b3d9990c921493a7234469293c73bc289176f" \
  -d '{"domain":"renunganbot.qzz.io"}'

# Check if email arrives (will timeout if domain blacklisted)
curl "https://tempmail.renunganbot.qzz.io/api/inbox/test@renunganbot.qzz.io/wait?timeout=10" \
  -H "X-Email-API-Key: ..."
```

## Migration History

- **Before:** 4 providers (DuckMail, YYDS, Cloudflare, CloudMail)
- **After:** TempMail only (self-hosted, custom domain)
- **Reason:** Need custom domain to avoid blacklist
- **Status:** Need NEW domain - current one already blacklisted

## Old Providers (Reference Only - All Blacklisted)

### DuckMail (api.duckmail.sbs)
```python
# Domains: @duck.com, @duck.email, etc
# Status: BLACKLISTED by x.ai
```

### YYDS Mail (vip.215.im)
```python
# Domains: Various Chinese domains
# Status: BLACKLISTED by x.ai
```

### Cloudflare Temp Email
```python
# Public Worker-based temp email
# Status: BLACKLISTED by x.ai
```

**Note:** Tidak bisa restore provider lama karena semua domainnya sudah di-blacklist.

## Next Steps

1. **Register domain baru** yang belum masuk blacklist
2. Setup Cloudflare DNS + Email Routing
3. Deploy Cloudflare Worker untuk forward email
4. Update TempMail config
5. Test registration

## Testing

```bash
# Test TempMail API
python test_real_api.py

# Test full registration (will fail if domain blacklisted)
echo "start" | python grok_register_ttk.py --cli
```

## Repository

https://github.com/jhopan/grok-register

---

**Last Updated:** 2026-08-31  
**Status:** ⚠️ Need new email domain (current blacklisted)  
**Priority:** HIGH - Project blocked until new domain acquired
