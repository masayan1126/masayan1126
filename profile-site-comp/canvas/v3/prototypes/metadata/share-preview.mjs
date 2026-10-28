const dataNode=document.querySelector('#share-preview-data');
if(dataNode){
  const snapshot=JSON.parse(dataNode.textContent);
  const root=document.querySelector('#share-preview');
  const picker=root.querySelector('#share-page');
  const feedback=root.querySelector('#share-feedback');
  const fallback=root.querySelector('#share-copy-fallback');
  const cards=root.querySelector('#share-cards');
  const sourceHost=new URL(snapshot.source).host;
  let current=null;
  function safeUrl(value,base=snapshot.source){
    const url=new URL(value,base);
    if(url.protocol!=='https:'||url.host!==sourceHost)throw new Error('取得先URLを確認できませんでした。');
    return url.href;
  }
  function addValue(label,value){
    const dt=document.createElement('dt'),dd=document.createElement('dd');
    dt.textContent=label;dd.textContent=value||'未設定';
    root.querySelector('#share-values').append(dt,dd);
  }
  function render(){
    current=snapshot.pages.find(row=>row.key===picker.value);
    feedback.textContent='';fallback.hidden=true;
    const error=root.querySelector('#share-error');
    error.hidden=true;cards.hidden=true;
    for(const id of ['#share-live-page','#share-live-image']){
      const link=root.querySelector(id);link.hidden=true;link.removeAttribute('href');
    }
    root.querySelector('#share-values').replaceChildren();
    root.querySelector('#share-captured').textContent=`公開情報の取得：${new Intl.DateTimeFormat('ja-JP',{dateStyle:'medium',timeStyle:'medium',timeZone:'Asia/Tokyo'}).format(new Date(snapshot.fetched_at))}（日本時間）`;
    if(!current?.ok){
      error.textContent='このページの公開情報を取得できませんでした。';error.hidden=false;
      root.querySelector('#share-live-page').hidden=true;root.querySelector('#share-live-image').hidden=true;
      root.querySelector('#share-copy').disabled=true;
      root.querySelector('#share-http').textContent=current?.error||'取得データがありません。';
      return;
    }
    try{
      const pageUrl=safeUrl(current.response.final_url);
      const tags=current.tags;
      const ogUrl=tags['og:image']?safeUrl(tags['og:image'],pageUrl):null;
      const twitterUrl=tags['twitter:image']?safeUrl(tags['twitter:image'],pageUrl):null;
      cards.querySelectorAll('[data-page-link]').forEach(link=>link.href=pageUrl);
      root.querySelector('#share-live-page').href=pageUrl;root.querySelector('#share-live-page').hidden=false;
      const imageLink=root.querySelector('#share-live-image');imageLink.hidden=!ogUrl;if(ogUrl)imageLink.href=ogUrl;else imageLink.removeAttribute('href');
      root.querySelector('#share-copy').disabled=false;
      cards.querySelectorAll('[data-share-domain]').forEach(node=>node.textContent=new URL(pageUrl).host);
      cards.querySelectorAll('[data-share-text]').forEach(node=>{
        node.textContent=tags[node.dataset.shareText]||'未設定';
        node.title=node.textContent;
      });
      cards.querySelectorAll('[data-share-img]').forEach(image=>{
        const isTwitter=image.dataset.shareImg==='twitter';
        const url=isTwitter?twitterUrl:ogUrl;
        const warning=image.closest('.share-stage').querySelector('.share-image-error');
        warning.hidden=true;
        image.alt=tags[isTwitter?'twitter:image:alt':'og:image:alt']||'公開ページの共有画像';
        image.onload=()=>{warning.hidden=true;};
        image.onerror=()=>{warning.hidden=false;};
        if(url){image.hidden=false;image.src=url;}
        else{image.hidden=true;image.removeAttribute('src');warning.hidden=false;}
      });
      const image=ogUrl&&current.images[ogUrl];
      root.querySelector('#share-image-spec').textContent=image?`${image.width}×${image.height}px · ${(image.bytes/1024).toFixed(1)}KB · HTTP ${image.status}`:'画像情報なし';
      root.querySelector('#share-http').textContent=`HTML：HTTP ${current.response.status} ／ ${current.response.content_type}`;
      addValue('取得元',current.response.url);addValue('転送後',current.response.final_url);
      addValue('正規URL',current.canonical);addValue('ページタイトル',current.title);addValue('description',tags.description);addValue('favicon',current.favicon);
      for(const name of ['og:title','og:description','og:url','og:image','og:image:alt','og:image:width','og:image:height','twitter:card','twitter:title','twitter:description','twitter:image','twitter:image:alt'])addValue(name,tags[name]);
      if(image)addValue('画像のSHA-256',image.sha256);
      if(current.missing.length){error.textContent=`未設定の項目：${current.missing.join('、')}`;error.hidden=false;}
      cards.hidden=false;
    }catch(problem){error.textContent=problem.message;error.hidden=false;root.querySelector('#share-copy').disabled=true;}
  }
  root.querySelector('form').addEventListener('submit',event=>event.preventDefault());
  picker.addEventListener('change',render);
  root.querySelectorAll('[name="share-width"]').forEach(radio=>radio.addEventListener('change',()=>{cards.dataset.width=radio.value;}));
  root.querySelector('#share-copy').addEventListener('click',async()=>{
    if(!current?.ok)return;
    const value=safeUrl(current.response.final_url);
    try{await navigator.clipboard.writeText(value);feedback.textContent='公開URLをコピーしました。';}
    catch{fallback.hidden=false;const input=root.querySelector('#share-copy-value');input.value=value;input.focus();input.select();feedback.textContent='下の欄からURLをコピーしてください。';}
  });
  render();
}
