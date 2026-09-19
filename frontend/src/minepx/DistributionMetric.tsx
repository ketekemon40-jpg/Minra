import {useEffect,useState} from 'react';
import {Coins} from 'lucide-react';
import {request} from './api';
import {Reward} from './types';

export const DistributionMetric=()=>{
 const [total,setTotal]=useState<string|null>(null);
 useEffect(()=>{
  let active=true;
  const refresh=async()=>{
   try{const info=await request<Reward>('/rewards');if(active)setTotal(info.distribution_scope==='all_holders'?info.total_distributed_gldx:null);}
   catch{if(active)setTotal(null);}
  };
  refresh();const timer=setInterval(refresh,60000);
  return()=>{active=false;clearInterval(timer);};
 },[]);
 const numeric=total===null?NaN:Number(total);
 const value=Number.isFinite(numeric)&&numeric>=0?new Intl.NumberFormat('en-US',{notation:numeric>=1000000?'compact':'standard',maximumFractionDigits:6}).format(numeric):'—';
 return <div className="world-metric" data-testid="distribution-metric" title={`Total GLDx distributed to all holders via Stonk.fun${value!=='—'?`: ${total} GLDx`:''}`}>
  <div className="metric-icon gold"><Coins size={19}/></div>
  <div><span data-testid="metric-distribution-label">Distribution</span><strong className="metric-unavailable" data-testid="metric-distribution-total">{value} <small>GLDx</small></strong></div>
 </div>;
};