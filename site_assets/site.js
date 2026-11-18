/* Kestrel interactive interface: plain JavaScript, no dependencies. */
(function(){
  "use strict";
  const reducedMotion=window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const onReady=(callback)=>document.readyState==="loading"?document.addEventListener("DOMContentLoaded",callback,{once:true}):callback();
  onReady(function(){
    // Clear mobile menu for a true multi-page website.
    const menuButton=document.querySelector("[data-menu-toggle]");
    const nav=document.querySelector("#primary-nav");
    if(menuButton && nav){
      const closeMenu=()=>{
        nav.classList.remove("is-open");
        menuButton.setAttribute("aria-expanded","false");
      };
      menuButton.addEventListener("click",()=>{
        const opened=nav.classList.toggle("is-open");
        menuButton.setAttribute("aria-expanded",String(opened));
      });
      nav.querySelectorAll("a").forEach(link=>link.addEventListener("click",closeMenu));
      document.addEventListener("keydown",event=>{
        if(event.key==="Escape")closeMenu();
      });
    }
    const path=window.location.pathname.replace(/\/+$/,"/") || "/";
    document.querySelectorAll(".site-nav a").forEach(link=>{
      const target=new URL(link.href,window.location.origin).pathname.replace(/\/+$/,"/") || "/";
      if(path===target || (target.endsWith("/systems/") && path.startsWith(target))){
        link.setAttribute("aria-current","page");
      }
    });

    // Reusable entrance animation. Content stays accessible without JavaScript.
    if(!reducedMotion && "IntersectionObserver" in window){
      document.documentElement.classList.add("js-enhanced");
      const observer=new IntersectionObserver((entries)=>{
        for(const entry of entries){
          if(entry.isIntersecting){entry.target.classList.add("is-visible");observer.unobserve(entry.target);}
        }
      },{threshold:.08,rootMargin:"0px 0px -24px 0px"});
      document.querySelectorAll("[data-reveal]").forEach(el=>observer.observe(el));
    }

    // Filter actual generated programme groups by label and market.
    const input=document.querySelector("[data-programme-search]");
    const cards=Array.from(document.querySelectorAll("[data-programme-card]"));
    const buttons=Array.from(document.querySelectorAll("[data-market-filter]"));
    const status=document.querySelector("[data-results-status]");
    const empty=document.querySelector("[data-empty-state]");
    if(cards.length){
      let market="all";
      const update=()=>{
        const term=(input?input.value:"").trim().toLowerCase();
        let visible=0;
        cards.forEach((card)=>{
          const words=(card.dataset.search||"").toLowerCase();
          const markets=(card.dataset.markets||"").toLowerCase().split("|");
          const match=words.includes(term)&&(market==="all"||markets.includes(market));
          card.hidden=!match;
          if(match)visible++;
        });
        if(status)status.textContent=visible+" programme group"+(visible===1?"":"s")+" shown";
        if(empty)empty.hidden=visible>0;
      };
      if(input)input.addEventListener("input",update);
      buttons.forEach((button)=>{
        button.addEventListener("click",()=>{
          market=button.dataset.marketFilter||"all";
          buttons.forEach(btn=>btn.setAttribute("aria-pressed",String(btn===button)));
          update();
        });
      });
      update();
    }

    // Real build audit. Values are filled only from the published JSON report.
    const audit=document.querySelector("[data-audit-feed]");
    if(audit){
      const set=(selector,value)=>{const el=audit.querySelector(selector);if(el)el.textContent=value;};
      const url=audit.dataset.auditFeed;
      fetch(url,{cache:"no-store",headers:{"Accept":"application/json"}})
        .then(res=>{if(!res.ok)throw new Error("Report fetch returned "+res.status);return res.json();})
        .then(data=>{
          if(!data || typeof data.pages_checked!=="number" || !data.counts || !Number.isFinite(Number(data.counts.error))){
            throw new Error("Unexpected audit response shape");
          }
          const errs=Number(data.counts.error);
          const warnings=Number(data.counts.warning||0);
          set("[data-audit-pages]",String(data.pages_checked));
          set("[data-audit-errors]",String(errs));
          set("[data-audit-status]",errs>0?"Attention required":"Release checks completed");
          set("[data-audit-footnote]",warnings+" warning"+(warnings===1?"":"s")+" · Audit generated "+String(data.created_at||"date unknown"));
          audit.dataset.health=errs>0?"attention":"ok";
        })
        .catch(()=>{
          set("[data-audit-pages]","—");
          set("[data-audit-errors]","—");
          set("[data-audit-status]","Live report unavailable");
          set("[data-audit-footnote]","Open the published report or GitHub Actions to inspect the latest available run.");
          audit.dataset.health="unknown";
        });
    }

    // A deterministic, explicitly simulated technical SEO diagnosis.
    const scenarios={
      noindex:{
        path:"/programmes/online-mba-ghana/",
        code:'<meta name="robots" content="noindex">',
        level:"CRITICAL · INDEXABILITY",
        title:"An important page is excluded",
        explanation:"A crawler can flag an unexpected noindex directive when the approved baseline expects this page to be indexable. Verify the intended publishing state before alerting engineering."
      },
      canonical:{
        path:"/programmes/online-mba-ghana/",
        code:'<link rel="canonical" href="https://example.org/unrelated-course/">',
        level:"ERROR · CANONICAL",
        title:"Canonical destination does not match",
        explanation:"Compare the canonical target with the approved URL map and page content. A mismatched canonical may cause search engines to prefer another address."
      },
      link:{
        path:"/programmes/online-marketing-nigeria/",
        code:'<a href="/programmes/removed-page/">Explore the course</a>\nHTTP/1.1 404 Not Found',
        level:"ERROR · BROKEN LINK",
        title:"Internal navigation leads to a 404",
        explanation:"An automated crawl can identify broken destinations. Resolve by updating the link, restoring the intended page or redirecting to a genuinely equivalent destination."
      }
    };
    const tabs=Array.from(document.querySelectorAll("[data-scenario]"));
    const render=(key)=>{
      const data=scenarios[key];
      if(!data)return;
      const fill=(selector,value)=>{const el=document.querySelector(selector);if(el)el.textContent=value;};
      fill("[data-scenario-path]",data.path);
      fill("[data-scenario-code]",data.code);
      fill("[data-scenario-level]",data.level);
      fill("[data-scenario-title]",data.title);
      fill("[data-scenario-explanation]",data.explanation);
      tabs.forEach(tab=>{const selected=tab.dataset.scenario===key;tab.setAttribute("aria-selected",String(selected));tab.tabIndex=selected?0:-1;});
    };
    tabs.forEach((tab,index)=>{
      tab.addEventListener("click",()=>render(tab.dataset.scenario));
      tab.addEventListener("keydown",(event)=>{
        if(!["ArrowRight","ArrowDown","ArrowLeft","ArrowUp","Home","End"].includes(event.key))return;
        event.preventDefault();
        const step=event.key==="ArrowRight"||event.key==="ArrowDown"?1:-1;
        const idx=event.key==="Home"?0:event.key==="End"?tabs.length-1:(index+step+tabs.length)%tabs.length;
        tabs[idx].focus();render(tabs[idx].dataset.scenario);
      });
    });
    if(tabs.length)render("noindex");
  });
})();