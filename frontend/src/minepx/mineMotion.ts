import {Agent,stages} from './types';
type Point={x:number;y:number};
const routes:Record<string,number[][]>={
 balanced:[[215,523],[343,323],[595,246],[790,385],[1048,492],[616,587]],
 deep:[[215,523],[927,317],[1056,271],[890,383],[1048,492],[616,587]],
 careful:[[215,523],[331,350],[383,292],[657,374],[1048,492],[616,587]],
};
export type MinerMotion={x:number;y:number;goal:Point;stage:number;phase:number;walking:boolean;speed:number;seed:number;facing:number;key:string;taskTime:number;localTrip:boolean};
const identitySeed=(id:string)=>{let h=2166136261;for(let i=0;i<id.length;i++)h=Math.imul(h^id.charCodeAt(i),16777619);return h>>>0;};
const taskStage=(agent:Agent)=>agent.status==='ready'?0:Math.max(0,stages.indexOf(agent.stage));
const pointFor=(agent:Agent,stage:number,seed:number):Point=>{
 const route=routes[agent.preference]||routes.balanced;
 return {x:route[stage][0]+seed%67-33,y:route[stage][1]+Math.floor(seed/67)%27-13};
};
export function createMotion(agent:Agent):MinerMotion{
 const seed=identitySeed(agent.id),stage=taskStage(agent),point=pointFor(agent,stage,seed);
 return {...point,goal:point,stage,phase:seed%100/10,walking:false,speed:0,seed,facing:1,key:'',taskTime:0,localTrip:false};
}
export function advanceMotion(state:MinerMotion,agent:Agent,elapsed:number,enabled:boolean){
 // Animation time is local and monotonic. API timestamps/order never reposition a visible miner.
 if(!enabled)return;
 const dt=Math.max(0,Math.min(elapsed,.05));
 const stage=taskStage(agent),key=`${agent.stage}:${agent.preference}:${agent.status}`;
 if(state.key!==key){state.goal=pointFor(agent,stage,state.seed);state.stage=stage;state.key=key;state.taskTime=0;state.localTrip=false;}
 state.phase+=dt;
 if(agent.status!=='active'){state.walking=false;state.speed=0;return;}
 const dx=state.goal.x-state.x,dy=state.goal.y-state.y,distance=Math.hypot(dx,dy);
 state.walking=distance>.15;
 if(state.walking){
  const cruise=state.localTrip?17:48+state.seed%6;
  const desired=Math.min(cruise,Math.max(8,distance*2.3));
  state.speed+=(desired-state.speed)*(1-Math.exp(-dt*7));
  const travel=Math.min(distance,Math.min(state.speed,54)*dt);
  state.x+=dx/distance*travel;state.y+=dy/distance*travel;
  if(Math.abs(dx)>3)state.facing=dx>=0?1:-1;
  state.taskTime=0;
 }else{
  state.speed=0;state.taskTime+=dt;
  // Work never freezes while the next server decision is pending: miners swing, survey or handle ore.
  // Brief local repositioning stays beside the current workstation, not a random map teleport.
  const duration=state.stage===2?3.5:state.stage===5?4:2.8;
  if(state.taskTime>duration){
   const anchor=pointFor(agent,state.stage,state.seed),cycle=Math.floor(state.phase/duration);
   state.goal={x:anchor.x+Math.sin(cycle*1.7+state.seed)*14,y:anchor.y+Math.cos(cycle*1.1)*5};
   state.taskTime=0;state.localTrip=true;
  }
 }
}