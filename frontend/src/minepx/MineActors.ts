import {Container,Graphics,Sprite,Text,Texture,Rectangle} from 'pixi.js';
import {Agent} from './types';
import {minerTexture} from './sprites';
import {createMotion,advanceMotion,MinerMotion} from './mineMotion';
export type MinerActor={root:Container;figure:Container;body:Sprite;tool:Graphics;cart:Graphics;spark:Graphics;label:Text;motion:MinerMotion;textures:Texture[]};
export const createMinerActor=(agent:Agent,textures:Texture[],onClick:()=>void):MinerActor=>{
 const root=new Container(),figure=new Container();root.label=agent.id;root.eventMode='static';root.cursor='pointer';root.hitArea=new Rectangle(-28,-46,62,64);root.on('pointertap',onClick);
 const frames=[0,1,2].map(p=>{const t=Texture.from(minerTexture(agent.avatar,p));t.source.scaleMode='nearest';textures.push(t);return t;});
 root.addChild(new Graphics().ellipse(0,6,22,7).fill({color:0x090c0b,alpha:.35}));root.addChild(figure);
 const body=new Sprite(frames[0]);body.anchor.set(.5,.85);body.scale.set(1.18);figure.addChild(body);
 const tool=new Graphics().rect(-2,-12,3,23).fill(0x9e7851).rect(-11,-15,19,4).fill(0xb8c2c3).rect(5,-11,4,4).fill(0x78888b);tool.position.set(19,-13);figure.addChild(tool);
 const cart=new Graphics().rect(22,-7,28,13).fill(0x333d40).rect(21,-8,30,3).fill(0x89908a).rect(25,-15,7,7).fill(0xb3944f).rect(33,-18,6,10).fill(0xd6b45e).rect(40,-14,6,7).fill(0xc19b47).rect(25,5,6,6).fill(0x232b30).rect(41,5,6,6).fill(0x232b30).rect(24,-3,24,2).fill(0x5f6a69);figure.addChild(cart);
 const spark=new Graphics();for(let j=0;j<3;j++)spark.rect(21+j*5,-6-j*3,2,2).fill({color:0xf8ca68,alpha:.8-j*.15});figure.addChild(spark);
 const label=new Text({text:agent.name,style:{fontFamily:'JetBrains Mono, monospace',fontSize:12,fill:agent.is_bot?0xe0dfd3:0xf7cf7b,stroke:{color:0x151819,width:4},fontWeight:'500'}});label.anchor.set(.5,1);label.position.set(0,-42);root.addChild(label);
 const motion=createMotion(agent);root.position.set(motion.x,motion.y);
 return {root,figure,body,tool,cart,spark,label,motion,textures:frames};
};
export function updateMinerActor(item:MinerActor,agent:Agent,dt:number,enabled:boolean){
 const m=item.motion;advanceMotion(m,agent,dt,enabled);
 const working=agent.status==='active',walking=m.walking&&working,t=m.phase;
 item.root.position.set(m.x,m.y);item.root.zIndex=m.y;
 item.figure.scale.x=m.facing;
 item.body.texture=item.textures[walking?1+Math.floor(t*8)%2:0];
 item.figure.y=working?(walking?Math.sin(t*14)*1.35:Math.sin(t*3.4)*.8):0;
 item.body.rotation=working&&!walking?Math.sin(t*(m.stage===2?7:3))*.035:0;
 item.tool.visible=working;
 item.tool.rotation=walking?Math.sin(t*9)*.16+.35:Math.sin(t*(m.stage===2?7:m.stage===5?4:2.5))*(m.stage===2?.95:.35);
 item.cart.visible=working&&(m.stage===3||m.stage===4);
 item.cart.y=working?Math.sin(t*(walking?14:4))*.7:0;
 item.spark.visible=working&&!walking&&(m.stage===2||m.stage===5)&&Math.sin(t*7)>.65;
 item.spark.alpha=.4+Math.max(0,Math.sin(t*7))*.6;
 item.body.tint=agent.status==='paused'?0x9b9b9b:0xffffff;
 if(item.label.text!==agent.name)item.label.text=agent.name;
}