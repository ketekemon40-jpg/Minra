import {useCallback,useEffect,useState} from 'react';
import {Reward} from './types';
import {accessToken,request} from './api';
import {useWallet} from './WalletContext';
export type ReceiptHistory={wallet_address:string;asset:string;total_received:string|null;receipt_count:number;last_received_at:string|null;observed_at:string|null;chain_connected:boolean;transactions:{signature:string;amount:string;received_at:string;source:string}[]};
export function useRewardData(){
 const {wallet}=useWallet(),walletId=wallet?.wallet_id;
 const [info,setInfo]=useState<Reward|null>(null),[history,setHistory]=useState<ReceiptHistory|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(true),[revision,setRevision]=useState(0);
 useEffect(()=>{let live=true;setHistory(null);setError('');setLoading(true);const token=accessToken();
  Promise.all([request<Reward>('/rewards'),walletId?request<ReceiptHistory>('/rewards/receipts'):Promise.resolve(null)]).then(([metadata,receipts])=>{if(live&&token===accessToken()){setInfo(metadata);setHistory(receipts);}}).catch(()=>{if(live)setError('Receipt information could not be loaded. Please try again.');}).finally(()=>{if(live)setLoading(false);});
  return()=>{live=false;};
 },[walletId,revision]);
 const refresh=useCallback(()=>setRevision(v=>v+1),[]);
 return {info,history:history?.wallet_address===wallet?.address?history:null,error,loading,refresh,wallet};
}