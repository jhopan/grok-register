# Old Email Providers Reference (All Blacklisted)

⚠️ **WARNING:** Semua provider ini sudah di-blacklist oleh accounts.x.ai  
Dokumen ini hanya untuk referensi jika mau test manual atau pakai untuk service lain.

---

## 1. DuckMail (api.duckmail.sbs)

### Signup
https://api.duckmail.sbs/register (atau check dokumentasi mereka)

### API Endpoints
```
BASE_URL: https://api.duckmail.sbs/v1
Auth: Bearer token atau API key di header
```

### Usage
```bash
# Create email
curl -X POST https://api.duckmail.sbs/v1/inbox \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"

# Get messages
curl https://api.duckmail.sbs/v1/inbox/{email}/messages \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Domains
- @duck.com
- @duck.email
- @duckmail.com
- (dan domain lain yang mereka support)

### Status
❌ **BLACKLISTED by x.ai** - tidak bisa dipakai untuk accounts.x.ai

---

## 2. YYDS Mail (vip.215.im)

### Signup
https://vip.215.im (Chinese service)

### API Endpoints
```
BASE_URL: https://api.215.im
Auth: API key di query params atau header
```

### Usage
```bash
# Create mailbox
curl -X POST https://api.215.im/create \
  -d "api_key=YOUR_KEY"

# Check messages
curl https://api.215.im/messages/{mailbox_id}?api_key=YOUR_KEY
```

### Domains
Various Chinese domains (berubah-ubah)

### Status
❌ **BLACKLISTED by x.ai** - tidak bisa dipakai untuk accounts.x.ai

---

## 3. Cloudflare Temp Email

### Setup
Deploy Cloudflare Worker dengan Email Routing:

```javascript
// worker.js
export default {
  async email(message, env, ctx) {
    // Store email in KV or D1
    const email = {
      to: message.to,
      from: message.from,
      subject: message.headers.get('subject'),
      body: await new Response(message.raw).text()
    };
    
    await env.EMAILS.put(message.to, JSON.stringify(email));
  }
}
```

### API untuk retrieve
```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const email = url.pathname.split('/').pop();
    const data = await env.EMAILS.get(email);
    return new Response(data);
  }
}
```

### Domains
Public Cloudflare Worker domains atau domain sendiri

### Status
❌ **Public domains BLACKLISTED** - domain public sudah di-blacklist
⚠️ **Custom domain MIGHT work** - tapi renunganbot.qzz.io sudah kena blacklist juga

---

## 4. Mail.tm (mail.tm)

### Free Public API
```
BASE_URL: https://api.mail.tm
No auth needed for basic usage
```

### Usage
```bash
# Get available domains
curl https://api.mail.tm/domains

# Create account
curl -X POST https://api.mail.tm/accounts \
  -H "Content-Type: application/json" \
  -d '{"address":"test@mail.tm","password":"password123"}'

# Get token
curl -X POST https://api.mail.tm/token \
  -H "Content-Type: application/json" \
  -d '{"address":"test@mail.tm","password":"password123"}'

# Get messages
curl https://api.mail.tm/messages \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Domains
- @mail.tm
- (check /domains endpoint untuk list lengkap)

### Status
❌ **LIKELY BLACKLISTED** - service public terkenal, hampir pasti sudah di-blacklist

---

## 5. Guerrilla Mail (guerrillamail.com)

### Free Public API
```
BASE_URL: https://api.guerrillamail.com/ajax.php
No API key needed
```

### Usage
```bash
# Get email address
curl "https://api.guerrillamail.com/ajax.php?f=get_email_address"

# Check inbox
curl "https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token=YOUR_TOKEN"
```

### Status
❌ **BLACKLISTED** - service paling terkenal, pasti sudah di-blacklist

---

## Test Manual Providers

Untuk test apakah domain di-blacklist:

```bash
# 1. Daftar manual di https://accounts.x.ai/sign-up
# 2. Klik "Sign up with email"
# 3. Input email dari provider yang mau ditest
# 4. Lihat response:
#    - "Invalid email" atau langsung reject = BLACKLISTED
#    - Email dikirim tapi tidak sampai = Domain routing issue
#    - Email sampai dan bisa verify = WORKING (rare!)
```

---

## Kesimpulan

**SEMUA public temp email provider sudah di-blacklist oleh x.ai.**

**Solusi yang mungkin:**
1. **Domain baru yang belum masuk blacklist** (paling reliable)
   - Beli domain murah ($1-5/year)
   - Setup Email Routing
   - Pakai untuk TempMail server kamu
   
2. **Gmail/Outlook dengan + trick** (might work)
   - yourname+random123@gmail.com
   - Tapi butuh banyak base account
   
3. **Subdomain dari domain legit**
   - mail.your-business.com
   - inbox.your-project.com
   - Terlihat lebih "real"

4. **Namecheap/Namesilo email forwarding** (cheap)
   - Domain $1-2/year
   - Free email forwarding
   - Forward ke TempMail server

**Recommendation:** 
Beli domain murah khusus untuk ini (Namecheap/Namesilo ~$1/year), setup Email Routing, pakai untuk TempMail server. Satu-satunya cara yang sustainable.
