// Browser smoke test (manual): run API on :18380, listener on :18381 and 'vite --port 13000' with
// VITE_DEV_API=http://127.0.0.1:18380 and ADMIN_TOKEN=adm-0123456789abcdef01234567, then:
//   SHOT=/tmp/dash.png NODE_PATH=$(npm root -g) node tests/e2e/ui_smoke.cjs
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => m.type()==='error' && errs.push(m.text()));
  await p.goto('http://127.0.0.1:13000');
  await p.fill('#admin-token', 'wrong-token-wrong-token-wrong'); await p.click('text=Sign in');
  await p.waitForSelector('text=Invalid admin token');
  await p.fill('#admin-token', 'adm-0123456789abcdef01234567'); await p.click('text=Sign in');
  await p.waitForSelector('text=Live Alert Dashboard');
  await p.click('text=New Token'); await p.fill('#token-name', 'Prod kubeconfig'); await p.click('button:has-text("Fake Kubeconfig")');
  await p.click('button:has-text("Create Token")');
  await p.waitForSelector('td:has-text("Prod kubeconfig")');
  const url = await p.inputValue('tbody input'); console.log('trap url:', url);
  const r = await fetch(url.replace('18381','18381')); console.log('trap status', r.status);
  await p.click('text=Dashboard'); await p.waitForSelector('text=Top sources', { timeout: 10000 });
  await p.waitForSelector('text=Prod kubeconfig');
  await p.screenshot({ path: process.env.SHOT });
  console.log('console errors:', JSON.stringify(errs)); await b.close();
})();
