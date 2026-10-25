const { chromium } = require('../.tools/browser/node_modules/playwright');
const fs = require('fs');
const assert = require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1080},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const results=[];const pass=name=>{results.push(name);console.log('LULUS '+name);};
 try {
  await page.goto('http://127.0.0.1:8765/');
  await page.screenshot({path:'docs/evidence/ui-awal.png',fullPage:true});
  assert.equal(await page.locator('#processes tr').count(),3);pass('contoh tiga proses dan halaman awal');
  await page.click('#run-cpu');await page.waitForSelector('.cpu-result');
  assert.match(await page.locator('.cpu-result').innerText(),/3,33/);pass('FCFS tampil dengan hasil contoh manual');
  await page.screenshot({path:'docs/evidence/ui-fcfs.png',fullPage:true});
  await page.selectOption('#algorithm','compare');await page.click('#run-cpu');
  await page.waitForFunction(()=>document.querySelectorAll('.cpu-result').length===2);
  assert.match(await page.locator('.cpu-result').nth(1).innerText(),/Round Robin/);pass('perbandingan dua algoritma');
  await page.screenshot({path:'docs/evidence/ui-perbandingan.png',fullPage:true});
  await page.selectOption('#algorithm','rr');await page.click('#run-cpu');
  await page.waitForFunction(()=>document.querySelectorAll('.cpu-result').length===1 && document.querySelector('.cpu-result').textContent.includes('Round Robin'));
  await page.screenshot({path:'docs/evidence/ui-rr.png',fullPage:true});pass('Round Robin tunggal');
  await page.locator('.burst').first().fill('0');await page.click('#run-cpu');
  assert.equal(await page.locator('#cpu-error').isVisible(),true);pass('input nol ditolak');
  await page.locator('.burst').first().fill('1.5');await page.click('#run-cpu');
  assert.match(await page.locator('#cpu-error').innerText(),/bilangan bulat/);pass('pecahan ditolak');
  await page.click('#sample');await page.locator('.pid').first().fill('IDLE');await page.click('#run-cpu');
  assert.match(await page.locator('#cpu-error').innerText(),/IDLE/);pass('nama IDLE ditolak');
  await page.screenshot({path:'docs/evidence/ui-validasi.png',fullPage:true});
  await page.click('#sample');await page.click('#add');assert.equal(await page.locator('#processes tr').count(),4);
  await page.locator('.delete').last().click();assert.equal(await page.locator('#processes tr').count(),3);pass('tambah dan hapus proses');
  await page.click('#run-cpu');await page.waitForSelector('.cpu-result');
  const downloadPromise=page.waitForEvent('download');await page.click('#export-cpu');const download=await downloadPromise;assert.equal(download.suggestedFilename(),'hasil-penjadwalan.json');pass('ekspor hasil scheduling');
  await page.click('#tab-pc');assert.equal(await page.locator('#panel-cpu').isVisible(),false);
  await page.click('#run-pc');await page.waitForSelector('#buffer-slots');
  assert.equal(await page.locator('.slot').count(),5);pass('Producer–Consumer selesai dan buffer awal kosong');
  assert.match(await page.locator('#delay-note').innerText(),/jeda yang diminta, bukan waktu yang dijamin/);pass('jeda masukan dibedakan dari waktu aktual');
  await page.click('#next');
  assert.doesNotMatch(await page.locator('#event-caption strong').innerText(),/(Produsen|Konsumen)-1/);pass('aktor tunggal memakai label sederhana');
  await page.click('#previous');
  const maximum=Number(await page.locator('#replay-range').getAttribute('max'));
  let peak=0,peakIndex=0;
  for(let i=1;i<=maximum;i++){
   await page.locator('#replay-range').evaluate((el,n)=>{el.value=n;el.dispatchEvent(new Event('input'));},i);
   const count=await page.locator('.slot.filled').count();assert.ok(count<=5);
   if(count>peak){peak=count;peakIndex=i;}
  }
  assert.equal(await page.locator('.slot.filled').count(),0);pass('seluruh langkah buffer terjaga dan akhir kosong');
  await page.locator('#replay-range').evaluate((el,n)=>{el.value=n;el.dispatchEvent(new Event('input'));},peakIndex);
  await page.screenshot({path:'docs/evidence/ui-buffer.png',fullPage:true});
  await page.click('#play');await page.waitForTimeout(700);assert.equal(await page.locator('#play').innerText(),'Jeda');await page.click('#play');pass('putar ulang dan jeda');
  await page.click('#consumer-fast');await page.click('#run-pc');await page.waitForSelector('#buffer-slots');
  assert.match(await page.locator('#pc-output').innerText(),/Konsumen sempat menunggu/);pass('skenario konsumen cepat');
  await page.locator('#replay-range').evaluate(el=>{el.value='1';el.dispatchEvent(new Event('input'));});
  await page.screenshot({path:'docs/evidence/ui-konsumen.png',fullPage:true});
  await page.locator('#capacity').fill('0');await page.click('#run-pc');assert.equal(await page.locator('#pc-error').isVisible(),true);pass('kapasitas nol ditolak');
  await page.setViewportSize({width:390,height:844});await page.click('#tab-cpu');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:'docs/evidence/ui-mobile.png',fullPage:true});pass('layout mobile tanpa overflow halaman');
  await page.click('#tab-pc');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));pass('buffer mobile tanpa overflow halaman');
  await page.goto('http://127.0.0.1:8765/lanjutan.html');await page.waitForSelector('#sched-out .result');pass('materi tambahan tetap dapat dibuka');
  assert.deepEqual(errors,[]);pass('tidak ada error JavaScript');
  fs.writeFileSync('docs/evidence/browser-results.json',JSON.stringify({date:new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Jakarta'}).format(new Date()),timezone:'Asia/Jakarta',viewport:[1440,1080],mobile:[390,844],passed:results.length,checks:results,errors},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
