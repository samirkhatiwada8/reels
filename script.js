const input=document.getElementById('videoUrl'), statusBox=document.getElementById('status'), go=document.getElementById('goBtn');
document.getElementById('year').textContent=new Date().getFullYear();
function status(msg,type='info'){statusBox.textContent=msg;statusBox.className='status show '+type}
function validUrl(raw){try{const u=new URL(raw.trim());return ['http:','https:'].includes(u.protocol)?u:null}catch{return null}}
go.addEventListener('click', async()=>{
 const u=validUrl(input.value);
 if(!u){status('Paste a valid http:// or https:// video link first.','bad');return}
 go.disabled=true;go.textContent='Preparing download…';status('Connecting to the download service. Please keep this page open.','info');
 try{
  const res=await fetch('/api/download',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u.href})});
  const type=res.headers.get('content-type')||'';
  if(!res.ok||type.includes('application/json')){let data={};try{data=await res.json()}catch{}throw new Error(data.error||'Download failed. Try another public link.')}
  const blob=await res.blob();const cd=res.headers.get('content-disposition')||'';let filename='tau-video.mp4';const match=cd.match(/filename="?([^";]+)"?/i);if(match)filename=match[1];
  const blobUrl=URL.createObjectURL(blob),a=document.createElement('a');a.href=blobUrl;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(blobUrl),60000);status('Download ready. Check your browser downloads.','good');
 }catch(e){status(e.message||'Could not download this video. It may be private, unsupported, or blocked by the source.','bad')}
 finally{go.disabled=false;go.textContent='⬇ Start download'}
});
input.addEventListener('keydown',e=>{if(e.key==='Enter')go.click()});
