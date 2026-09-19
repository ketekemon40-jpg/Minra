import {useCallback,useEffect,useRef,useState} from 'react';
import {Agent,World,JournalEvent} from './types';
const API = process.env.REACT_APP_BACKEND_URL + '/api';
export const ACCESS_KEY='agent-miner-access';
export const accessToken=()=>sessionStorage.getItem(ACCESS_KEY);
type AgentEnvelope={agent:Agent|null};
export class ApiError extends Error { constructor(message:string,public status:number){super(message);} }
export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
 const token=accessToken();
 const response=await fetch(API+path,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`} : {}),...options.headers}});
 const data=await response.json();
 if(!response.ok){
  if(response.status===401&&token===accessToken()&&token){sessionStorage.removeItem(ACCESS_KEY);window.dispatchEvent(new Event('wallet-session-expired'));}
  const detail=typeof data.detail==='string'?data.detail:Array.isArray(data.detail)?data.detail.map((d:{msg?:string})=>d.msg||'Invalid value').slice(0,3).join(' · '):'Please try again.';
  throw new ApiError(detail,response.status);
 }
 return data;
}
export async function ensureSession(){if(!accessToken())throw new Error('Connect your wallet to continue.');}
export function useMine(walletId?:string){
 const [world,setWorld]=useState<World|null>(null),[agent,setAgent]=useState<Agent|null>(null),[events,setEvents]=useState<JournalEvent[]>([]),[error,setError]=useState(''),[loadedAccount,setLoadedAccount]=useState<string>();
 const generation=useRef(0);
 const refresh=useCallback(async()=>{
  const current=generation.current,token=accessToken();
  try{
   const [w,j]=await Promise.all([request<World>('/world'),request<JournalEvent[]>('/journal?limit=40')]);
   setWorld(w);setEvents(j);setError('');
   if(walletId&&token){const me=await request<AgentEnvelope>('/agent');if(current===generation.current&&token===accessToken()){setAgent(me.agent);setLoadedAccount(walletId);}}
  }catch(e){if(!(e instanceof ApiError&&e.status===401))setError((e as Error).message);}
 },[walletId]);
 useEffect(()=>{generation.current+=1;setAgent(null);setLoadedAccount(undefined);refresh();const id=setInterval(refresh,4000);return()=>{generation.current+=1;clearInterval(id);};},[refresh]);
 return {world,agent:loadedAccount===walletId?agent:null,events,error,refresh,setAgent,loadedAccount};
}