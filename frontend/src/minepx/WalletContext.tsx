import {createContext,useCallback,useContext,useEffect,useState,ReactNode} from 'react';
import {ACCESS_KEY,accessToken,ApiError,request} from './api';

export type WalletAccount={wallet_id:string;address:string;provider:string;holder_amount:number;eligible:boolean;network:string;mode:string};
type SavedWallet={wallet_id:string;address:string;provider:string;recovery_capability:string};
type WalletState={wallet:WalletAccount|null;saved:SavedWallet[];busy:boolean;loading:boolean;connect:(provider:string,id?:string)=>Promise<void>;disconnect:()=>Promise<void>};
const STORE='agent-miner-wallets';
const Context=createContext<WalletState|null>(null);
const readSaved=():SavedWallet[]=>{try{const value=JSON.parse(localStorage.getItem(STORE)||'[]');return Array.isArray(value)?value.filter(w=>typeof w.wallet_id==='string'&&typeof w.recovery_capability==='string'):[];}catch{return [];}};
export const shortAddress=(address:string)=>address.slice(0,4)+'…'+address.slice(-4);
export const WalletProvider=({children}:{children:ReactNode})=>{
 const [wallet,setWallet]=useState<WalletAccount|null>(null),[saved,setSaved]=useState<SavedWallet[]>(readSaved),[busy,setBusy]=useState(false),[loading,setLoading]=useState(!!accessToken());
 const clear=useCallback(()=>{sessionStorage.removeItem(ACCESS_KEY);setWallet(null);},[]);
 const walletId=wallet?.wallet_id;
 useEffect(()=>{let active=true;const restore=async()=>{if(!accessToken()){setLoading(false);return;}try{const account=await request<WalletAccount>('/session/me');if(active)setWallet(account);}catch(e){if(e instanceof ApiError&&e.status===401)clear();}finally{if(active)setLoading(false);}};restore();window.addEventListener('wallet-session-expired',clear);return()=>{active=false;window.removeEventListener('wallet-session-expired',clear);};},[clear]);
 useEffect(()=>{if(!walletId)return;const id=setInterval(()=>{const token=accessToken();request<WalletAccount>('/session/me').then(w=>{if(token===accessToken()&&w.wallet_id===walletId)setWallet(w);}).catch(()=>{});},10000);return()=>clearInterval(id);},[walletId]);
 const connect=async(provider:string,id?:string)=>{
  setBusy(true);
  try{
   let selected=id?saved.find(w=>w.wallet_id===id):saved.find(w=>w.provider===provider);
   if(!selected){
    const created=await request<WalletAccount&{recovery_capability:string}>('/wallets',{method:'POST',body:JSON.stringify({provider})});
    selected={wallet_id:created.wallet_id,address:created.address,provider:created.provider,recovery_capability:created.recovery_capability};
    const next=[...readSaved(),selected];localStorage.setItem(STORE,JSON.stringify(next));setSaved(next);
   }
   const data=await request<{token:string;wallet:WalletAccount}>('/session',{method:'POST',body:JSON.stringify({wallet_id:selected.wallet_id,recovery_capability:selected.recovery_capability})});
   sessionStorage.setItem(ACCESS_KEY,data.token);setWallet(data.wallet);
  }finally{setBusy(false);}
 };
 const disconnect=async()=>{setBusy(true);try{try{await request('/session/disconnect',{method:'POST'});}catch(e){if(!(e instanceof ApiError&&e.status===401))throw e;}clear();}finally{setBusy(false);}};
 return <Context.Provider value={{wallet,saved,busy,loading,connect,disconnect}}>{children}</Context.Provider>;
};
export const useWallet=()=>{const value=useContext(Context);if(!value)throw new Error('Wallet provider missing');return value;};