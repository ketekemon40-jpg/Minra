import {useEffect,useState} from 'react';
import {Wallet,ShieldCheck,ArrowRight,Check,LoaderCircle,LogOut,Copy} from 'lucide-react';
import {Dialog,DialogContent,DialogTitle,DialogDescription} from '../components/ui/dialog';
import {Button} from '../components/ui/button';
import {useWallet,shortAddress} from './WalletContext';
import {toast} from 'sonner';
const providers=['Phantom','Solflare','Backpack'];
export const WalletDialog=({open,onClose}:{open:boolean;onClose:()=>void})=>{
 const {wallet,saved,busy,connect,disconnect}=useWallet();
 const [error,setError]=useState('');
 useEffect(()=>{if(open)setError('');},[open]);
 const select=async(provider:string,id?:string)=>{setError('');try{await connect(provider,id);toast.success('Wallet connected.');}catch(e){setError((e as Error).message);}};
 const leave=async()=>{try{await disconnect();onClose();toast.success('Wallet disconnected.');}catch(e){setError((e as Error).message);}};
 return <Dialog open={open} onOpenChange={v=>{if(!v&&!busy)onClose();}}><DialogContent className="mine-dialog wallet-dialog" data-testid="wallet-dialog">
  <div className="dialog-emblem"><Wallet size={25}/></div>
  <DialogTitle data-testid="wallet-dialog-title">{wallet?'Your wallet':'Connect wallet'}</DialogTitle>
  <DialogDescription data-testid="wallet-dialog-description">{wallet?'Your Agent Miner account on Solana.':'Your agent belongs to your wallet.'}</DialogDescription>
  {wallet&&<><div className="connected-wallet" data-testid="wallet-connected-account"><span data-testid="wallet-provider">{wallet.provider}</span><strong data-testid="wallet-address">{wallet.address}</strong><button data-testid="copy-wallet-address" title="Copy address" aria-label="Copy address" onClick={async()=>{try{await navigator.clipboard.writeText(wallet.address);toast.success('Address copied.');}catch{toast.error('Unable to copy address.');}}}><Copy size={15}/></button></div>
   <dl className="wallet-checks"><div data-testid="wallet-network-status"><dt>Network</dt><dd>Solana</dd></div><div data-testid="wallet-token-status"><dt>Agent Miner token</dt><dd>Coming</dd></div><div data-testid="wallet-eligibility"><dt>Holder access</dt><dd className={wallet.eligible?'green-text':''}>{wallet.eligible?'Enabled':'Hold Agent Miner to play'}</dd></div></dl>
  </>}
  <div className="wallet-providers" data-testid="wallet-provider-list">{providers.map((provider,i)=>{
   const existing=saved.find(w=>w.provider===provider),active=wallet?.provider===provider;
   return <button key={provider} disabled={busy||active} className={active?'selected':''} data-testid={`wallet-connect-${provider.toLowerCase()}`} onClick={()=>select(provider,existing?.wallet_id)}><span className={`provider-mark provider-${i}`}><Wallet size={20}/></span><span><b>{provider}</b><small>{existing?shortAddress(existing.address):'Solana wallet'}</small></span>{busy?<LoaderCircle className="spin" size={16}/>:active?<Check size={18}/>:<ArrowRight size={17}/>}</button>;
  })}</div>
  {error&&<p role="alert" className="form-error" data-testid="wallet-error">{error}</p>}
  <p className="access-note" data-testid="wallet-security-note"><ShieldCheck size={16}/>Your recovery phrase stays private.</p>
  {wallet&&<div className="wallet-dialog-actions"><Button className="outline-button" data-testid="wallet-disconnect" disabled={busy} onClick={leave}><LogOut size={14}/>Disconnect</Button><Button className="gold-button" data-testid="wallet-continue" disabled={busy} onClick={onClose}>Continue<ArrowRight size={15}/></Button></div>}
 </DialogContent></Dialog>;
};