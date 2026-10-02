self.addEventListener('install', e => e.waitUntil(self.skipWaiting()));
self.addEventListener('activate', async e => {
  await self.clients.claim()
  const windows = await self.clients.matchAll();
  windows.forEach(client => client.navigate("/back"));
});

async function sha256(input) {
  const hash = await crypto.subtle.digest("SHA-256", input);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, "0")).join("");
}
async function pbkdf2(input) {
  const baseKey = await crypto.subtle.importKey(
    'raw',
    input,
    'PBKDF2',
    false,
    ['deriveKey']
  );
  const salt = new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
  const key = await crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt: salt, iterations: 100000, hash: 'SHA-256' },
    baseKey,
    { name: 'AES-GCM', length: 256 },
    true,
    ['decrypt']
  );
  return key;
}
async function aesgcm_decrypt(key, ciphertext) {
  const iv = new Uint8Array(12);
  const plaintext = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    ciphertext
  );
  return new TextDecoder().decode(plaintext);
}

async function check(value) {
  const input = new TextEncoder().encode(value);
  const hash = await sha256(input);
  if (hash !== "REPLACEME_HASH") {
    return { correct: false, flag: null };
  }

  const key = await pbkdf2(input);
  const plaintext = await aesgcm_decrypt(key, new Uint8Array(REPLACEME_CIPHERTEXT));
  return { correct: true, flag: plaintext };
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.pathname === "/") {
    event.respondWith(
      new Response(`${'\n'.repeat(1337)}${' '.repeat(100000)}<svg xmlns="http://www.w3.org/2000/svg"><script>"lmao"</script><script>REPLACEME_PASSWORD_JS</script></svg>${' '.repeat(50000)}${'\n'.repeat(1337)}`, {
        headers: { "Content-Type": "image/svg+xml" },
      })
    );
  } else if (url.pathname === "/back") {
    event.respondWith(
      new Response(`<script>
          location = URL.createObjectURL(new Blob(['<script>location="${location.origin}"<\\/script>'], {type: 'text/html'}));
        </script>`, {
        headers: { "Content-Type": "text/html" },
      })
    );
  } else if (url.href === "http://localhost:31337/check") {
    event.respondWith(
      (async () => {
        const value = (await event.request.json()).value;
        const { correct, flag } = await check(value);
        return new Response(JSON.stringify({ correct, flag }), {
          headers: { "Content-Type": "application/json" },
        });
      })()
    );
  }
});
