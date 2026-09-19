import {useEffect,useRef,useState} from 'react';
import {Application,Assets,Container,Sprite,Texture} from 'pixi.js';
import {Maximize,Minimize,Minus,Plus,LocateFixed,Eye,EyeOff,Pause,Play,Mountain} from 'lucide-react';
import {Agent,World} from './types';
import {createMinerActor,updateMinerActor,MinerActor} from './MineActors';
const W=1264,H=700;
export const MineScene=({world,onSelect}:{world:World|null;onSelect:(a:Agent)=>void})=>{
 const host=useRef<HTMLDivElement>(null),frame=useRef<HTMLDivElement>(null),latest=useRef(world),select=useRef(onSelect);
 const settings=useRef({zoom:1,labels:true,motion:true});
 const [zoom,setZoom]=useState(1),[labels,setLabels]=useState(true),[motion,setMotion]=useState(()=>!window.matchMedia('(prefers-reduced-motion: reduce)').matches),[full,setFull]=useState(false),[ready,setReady]=useState(false),[failed,setFailed]=useState(false);
 latest.current=world;select.current=onSelect;settings.current={zoom,labels,motion};
 useEffect(()=>{const listener=()=>setFull(Boolean(document.fullscreenElement));document.addEventListener('fullscreenchange',listener);return()=>document.removeEventListener('fullscreenchange',listener);},[]);
 useEffect(()=>{
  let cancelled=false,initialized=false,previousWorld:World|null=null,lastFrame=performance.now();
  const app=new Application(),sprites=new Map<string,MinerActor>(),textures:Texture[]=[];
  const visibility=()=>{lastFrame=performance.now();if(initialized){if(document.hidden)app.ticker.stop();else app.ticker.start();}};
  const run=async()=>{
   try{
    await app.init({width:W,height:H,background:0x17191b,antialias:false,resolution:1,preference:'webgl',roundPixels:false});initialized=true;
    if(cancelled){app.destroy(true);return;}
    host.current?.appendChild(app.canvas);app.canvas.setAttribute('data-testid','mine-canvas');app.canvas.setAttribute('role','img');app.canvas.setAttribute('aria-label','Live underground mine with autonomous pixel miners');
    // Read-only render telemetry permits measuring continuity without GPU pixel reads on every frame.
    Object.defineProperty(app.canvas,'minerSnapshot',{value:()=>[...sprites].map(([id,a])=>({id,x:a.root.x,y:a.root.y,phase:a.motion.phase,walking:a.motion.walking,tool:a.tool.rotation,stage:a.motion.stage,rendered_at:lastFrame}))});
    const terrain=await Assets.load('/assets/underground.jpg');if(cancelled)return;
    const scene=new Container();app.stage.addChild(scene);
    const bg=new Sprite(terrain);bg.width=W;bg.height=H;scene.addChild(bg);
    const actors=new Container();actors.sortableChildren=true;scene.addChild(actors);
    const embers=Array.from({length:7},(_,i)=>{const s=new Sprite(Texture.WHITE);s.width=3;s.height=3;s.tint=i%2?0xe3ac55:0xe8cd82;scene.addChild(s);return s;});
    let visualTime=0,previousZoom=1;
    app.ticker.maxFPS=60;
    app.ticker.add(()=>{
     if(cancelled)return;
     const frameNow=performance.now(),dt=Math.max(0,Math.min(.05,(frameNow-lastFrame)/1000));lastFrame=frameNow;
     const cfg=settings.current,data=latest.current;
     if(cfg.motion)visualTime+=dt;
     previousZoom+=(cfg.zoom-previousZoom)*(1-Math.exp(-dt*9));
     scene.scale.set(previousZoom);scene.position.set(W/2*(1-previousZoom),H/2*(1-previousZoom));
     if(!data)return;
     if(data!==previousWorld){
      const present=new Set(data.agents.map(a=>a.id));
      sprites.forEach((actor,id)=>{if(!present.has(id)){actor.root.destroy({children:true});sprites.delete(id);}});
      previousWorld=data;
     }
     const occupied:{x:number;y:number;w:number;h:number}[]=[];
     data.agents.forEach(agent=>{
      let actor=sprites.get(agent.id);
      if(!actor){actor=createMinerActor(agent,textures,()=>{const a=latest.current?.agents.find(a=>a.id===agent.id);if(a)select.current(a);});actors.addChild(actor.root);sprites.set(agent.id,actor);}
      updateMinerActor(actor,agent,dt,cfg.motion);
      const box={x:actor.root.x-actor.label.width/2-4,y:actor.root.y-58,w:actor.label.width+8,h:20};
      const clear=occupied.every(b=>box.x+box.w<b.x||box.x>b.x+b.w||box.y+box.h<b.y||box.y>b.y+b.h);
      actor.label.visible=cfg.labels;
      if(cfg.motion)actor.label.alpha+=((clear?1:.22)-actor.label.alpha)*(1-Math.exp(-dt*6));
      if(clear)occupied.push(box);
     });
     embers.forEach((ember,i)=>{const p=(visualTime*.26+i*.15)%1;ember.position.set(1065+Math.sin(i*12.5)*14,433-p*65);ember.alpha=(1-p)*.8;});
    });
    document.addEventListener('visibilitychange',visibility);visibility();setReady(true);
   }catch(e){if(!cancelled){setFailed(true);console.error('Mine renderer:',e);}}
  };
  run();
  return()=>{cancelled=true;document.removeEventListener('visibilitychange',visibility);if(initialized){app.destroy(true,{children:true,texture:false,textureSource:false});textures.forEach(t=>t.destroy(true));}};
 },[]);
 const fullscreen=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await frame.current?.requestFullscreen();}catch{setFull(false);}};
 return <section ref={frame} className={`mine-frame ${full?'is-fullscreen':''}`} data-testid="mine-world-panel">
  <div className="map-heading"><div className="section-title"><Mountain size={16}/><h2 data-testid="mine-map-title">The Underground</h2><span className="sector" data-testid="mine-sector">SECTOR 01</span></div><span className="live-tag" data-testid="map-live-status"><i/>{world?.worker_online?'LIVE WORLD':'CONNECTING'}</span></div>
  <div className="scene-wrap"><div ref={host} className="pixi-host" data-testid="mine-scene"/>
   {!ready&&<div className="scene-loading" data-testid="scene-loading"><Mountain size={28}/><span>{failed?'The mine view could not load. Please refresh.':'Opening the underground…'}</span></div>}
   <div className="map-coordinate" data-testid="map-coordinates"><span>THE BRASS HOLLOW</span><small>47° 12′ N · DEPTH 120 M</small></div>
   <div className="map-key" data-testid="map-legend"><i className="gold-dot"/>Gold seam<i className="teal-dot"/>Crystal vein</div>
   <div className="map-controls"><button data-testid="map-zoom-in" title="Zoom in" aria-label="Zoom in" disabled={zoom>=1.6} onClick={()=>setZoom(z=>Math.min(1.6,z+.2))}><Plus size={16}/></button><button data-testid="map-zoom-out" title="Zoom out" aria-label="Zoom out" disabled={zoom<=1} onClick={()=>setZoom(z=>Math.max(1,z-.2))}><Minus size={16}/></button><span/><button data-testid="map-reset-view" title="Reset view" aria-label="Reset view" onClick={()=>setZoom(1)}><LocateFixed size={16}/></button><button data-testid="map-fullscreen" title={full?'Exit full screen':'Full screen'} aria-label={full?'Exit full screen':'Full screen'} onClick={fullscreen}>{full?<Minimize size={16}/>:<Maximize size={16}/>}</button></div>
  </div>
  <div className="map-footer"><span data-testid="map-crew-count"><i className="status-dot"/>{world?.active_agents??'—'} agents on shift <span className="muted">· Shared world</span></span><div><button data-testid="map-toggle-labels" aria-label="Toggle miner names" aria-pressed={labels} title="Miner names" onClick={()=>setLabels(v=>!v)}>{labels?<Eye size={14}/>:<EyeOff size={14}/>}<span>Names</span></button><button data-testid="map-toggle-animation" aria-pressed={motion} title={motion?'Pause animation':'Resume animation'} aria-label={motion?'Pause animation':'Resume animation'} onClick={()=>setMotion(v=>!v)}>{motion?<Pause size={14}/>:<Play size={14}/>}<span>{motion?'Pause view':'Resume view'}</span></button></div></div>
 </section>;
};