const fs=require('fs');const path=require('path');
const {bundle}=require('@remotion/bundler');
const {selectComposition,openBrowser,renderStill,renderMedia}=require('@remotion/renderer');
const root=__dirname;process.chdir(root);fs.mkdirSync(path.join(root,'.cache/tmp'),{recursive:true});process.env.TMPDIR=path.join(root,'.cache/tmp');
(async()=>{
 const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),outDir:path.join(root,'.cache/bundle'),publicDir:path.join(root,'public')});
 const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
 const puppeteerInstance=await openBrowser('chrome',{browserExecutable});
 try{
 const composition=await selectComposition({serveUrl,id:'Full',puppeteerInstance});
 if(process.argv[2]==='stills'){
  const frames=process.argv.slice(3).map(Number);
  for(const frame of frames){const output=path.join(root,`evidence/frames/native-f${String(frame).padStart(4,'0')}.png`);await renderStill({serveUrl,composition,frame,output,puppeteerInstance,imageFormat:'png'});console.log('STILL',frame);}
 }else{
  let prior=-1;const range=process.argv[2]==='range'?process.argv.slice(3,5).map(Number):undefined;
  const outputLocation=path.join(root,range?'output/representative-v1.mp4':'output/deepinfer-fred-picture-render.mp4');
  await renderMedia({serveUrl,composition,outputLocation,codec:'h264',crf:16,pixelFormat:'yuv420p',audioCodec:'aac',audioBitrate:'320k',concurrency:2,puppeteerInstance,frameRange:range,onProgress:({progress})=>{const n=Math.floor(progress*100);if(n>=prior+5){console.log('RENDER',n);prior=n;}}});console.log('COMPLETE',outputLocation);
 }
 }finally{await puppeteerInstance.close({silent:true});}
})().catch(e=>{console.error(e);process.exit(1)});
