import {useState,useEffect} from 'react';
import {BrowserRouter,NavLink,Routes,Route,Link,useLocation} from 'react-router-dom';
import {Pickaxe,Compass,UserRound,Coins,BookOpen,Wallet,ArrowUpRight,Users,Layers3,Route as RouteIcon,ShieldCheck,ArrowRight,RefreshCw,Gem,Trophy,SlidersHorizontal} from 'lucide-react';
import {Toaster} from 'sonner';
import {Button} from '../components/ui/button';
import {useMine} from './api';
import {Agent,World} from './types';
import {MineScene} from './MineScene';
import {AgentPanel} from './AgentPanel';
import {AgentTelemetry} from './AgentTelemetry';
import Rewards,{PoolPanel} from './Rewards';
import Guide,{Collection} from './Guide';
import {Journal} from './Journal';
import {Crew} from './Crew';
import {AgentDialog} from './AgentDialog';
import {CrewDialog} from './Dialogs';
import {WalletDialog} from './WalletDialog';
import {WalletProvider,useWallet,shortAddress} from './WalletContext';
import StrategyPage from './StrategyPage';
import ContestPage from './ContestPage';
import './Strategy.css';
import './Wallet.css';
const nav=[{to:'/',label:'The Mine',icon:Compass,id:'mine'},{to:'/agent',label:'My Agent',icon:UserRound,id:'agent'},{to:'/leaderboard',label:'Contest',icon:Trophy,id:'contest'},{to:'/rewards',label:'Rewards',icon:Coins,id:'rewards'},{to:'/guide',label:'Field Guide',icon:BookOpen,id:'guide'}];
const Header=({onWallet}:{onWallet:()=>void})=>{
 const {pathname}=useLocation(),{wallet,loading}=useWallet();
 return <header className="site-header"><div className="header-inner"><Link to="/" className="brand" data-testid="brand-home" aria-label="Agent Miner home"><span className="brand-icon"><Pickaxe size={22}/><i/></span>Agent<span>Miner</span><small>AUTONOMOUS MINING</small></Link><nav aria-label="Main navigation">{nav.map(n=><NavLink className={({isActive})=>isActive||(n.id==='agent'&&pathname==='/strategy')?'active':''} key={n.id} to={n.to} end={n.to==='/'} data-testid={`nav-${n.id}`}><n.icon size={16}/>{n.label}</NavLink>)}</nav><div className="header-actions"><span className="chain-label" data-testid="chain-label"><Layers3 size={16}/>Solana</span><Button disabled={loading} data-testid="connect-wallet-button" className="wallet-button" onClick={onWallet}><Wallet size={15}/><span>{loading?'Connecting…':wallet?shortAddress(wallet.address):'Connect wallet'}</span></Button></div></div></header>;
};
const Metrics=({world}:{world:World|null})=><div className="world-metrics" data-testid="world-metrics">
 <div className="world-metric"><div className="metric-icon"><Users size={19}/></div><div><span data-testid="metric-agents-label">Agents on shift</span><div><strong data-testid="metric-active-agents">{world?.active_agents??'—'}</strong><small className="green-text" data-testid="metric-shift-status">IN THE MINE</small></div></div></div>
 <div className="world-metric"><div className="metric-icon"><Layers3 size={19}/></div><div><span data-testid="metric-ore-label">Ore collected</span><div><strong data-testid="metric-total-ore">{world?.ore_collected.toLocaleString('en-US')??'—'}</strong><small>ALL TIME</small></div></div></div>
 <div className="world-metric"><div className="metric-icon"><RouteIcon size={19}/></div><div><span data-testid="metric-expeditions-label">Expeditions completed</span><div><strong data-testid="metric-expeditions">{world?.expeditions.toLocaleString('en-US')??'—'}</strong></div></div></div>
 <div className="world-metric"><div className="metric-icon gold"><Coins size={19}/></div><div><span data-testid="metric-pool-label">GLDX holder pool<ArrowUpRight size={12}/></span><strong className="metric-unavailable" data-testid="metric-pool-balance">— <small>GLDX</small></strong></div></div>
</div>;
const Footer=({online}:{online:boolean})=><footer className="site-footer"><div data-testid="footer-copyright"><Pickaxe size={13}/><b>Agent Miner</b><span>Brass Hollow, Solana.</span></div><div data-testid="footer-status"><i className={online?'status-dot':'paused-dot'}/>{online?'World online':'Connecting to the mine'}<span>·</span><Link to="/guide" data-testid="footer-field-guide">Field guide<ArrowUpRight size={11}/></Link></div></footer>;
function Shell(){
 const identity=useWallet();
 const {world,agent,events,error,refresh,setAgent,loadedAccount}=useMine(identity.wallet?.wallet_id);
 const [create,setCreate]=useState(false),[walletOpen,setWalletOpen]=useState(false),[pendingCreate,setPendingCreate]=useState(false),[selected,setSelected]=useState<Agent|null>(null);
 const location=useLocation();
 useEffect(()=>{window.scrollTo(0,0);},[location.pathname]);
 useEffect(()=>{setCreate(false);},[identity.wallet?.wallet_id]);
 useEffect(()=>{if(pendingCreate&&identity.wallet?.eligible&&loadedAccount===identity.wallet.wallet_id){setWalletOpen(false);setPendingCreate(false);setCreate(!agent);}},[pendingCreate,identity.wallet?.wallet_id,identity.wallet?.eligible,loadedAccount,agent]);
 const openCreate=()=>{if(!identity.wallet?.eligible){setPendingCreate(true);setWalletOpen(true);}else if(loadedAccount!==identity.wallet.wallet_id){setPendingCreate(true);}else if(!agent)setCreate(true);};
 const closeWallet=()=>{setWalletOpen(false);setPendingCreate(false);};
 const update=(a:Agent)=>{setAgent(a);refresh();};
 const active=world?.agents.filter(a=>a.status==='active')||[];
 const playableAgent=identity.wallet?.eligible?agent:null;
 return <><Header onWallet={()=>setWalletOpen(true)}/><main className="app-main" key={location.pathname}>
 {error&&<div className="error-banner" role="alert" data-testid="connection-error"><span>{error}</span><button data-testid="retry-connection" onClick={refresh}><RefreshCw size={14}/>Retry</button></div>}
 <Routes>
 <Route path="/" element={<><div className="mine-page-heading"><div><div className="eyebrow" data-testid="mine-eyebrow"><span className="small-square"/>BRASS HOLLOW</div><h1 data-testid="mine-page-title">Agent Miner<span>.</span></h1><p data-testid="mine-page-subtitle">An open mine. A strategy that's yours.</p></div><div className="global-view" data-testid="public-view-status"><span><i className="status-dot"/>PUBLIC MINE</span><small>The next shift is already underway.</small></div></div><Metrics world={world}/><div className="dashboard-grid"><div className="world-column"><MineScene world={world} onSelect={setSelected}/><div className="world-caption" data-testid="world-caption"><span><Compass size={13}/>BRASS HOLLOW <span>—</span> THE FIRST EXPEDITION</span><Link to="/leaderboard" data-testid="discover-mine-lore">The underground league<ArrowRight size={13}/></Link></div></div><aside className="mine-sidebar"><AgentPanel agent={agent} onCreate={openCreate} onChange={update}/><PoolPanel/></aside></div><div className="activity-grid"><Journal events={events} agent={agent}/><Crew agents={active} onSelect={setSelected}/></div><div className="principle-strip" data-testid="mine-principles"><span><ShieldCheck size={15}/>Built around your wallet.</span><span>Holder rewards stay separate from contest prizes.<Link to="/rewards" data-testid="mine-reward-rules">Reward details<ArrowUpRight size={12}/></Link></span></div></>}/>
 <Route path="/agent" element={<div className="page-content"><div className="page-title"><div><div className="eyebrow" data-testid="agent-page-eyebrow">YOUR EXPEDITION</div><h1 data-testid="agent-page-title">My Agent<span>.</span></h1><p data-testid="agent-page-description">{agent?`${agent.name} at Brass Hollow.`:'A place on the next shift.'}</p></div><Link to="/" data-testid="agent-view-world" className="text-button">Back to the mine<ArrowUpRight size={15}/></Link></div><div className="agent-subnav"><span className="active" data-testid="agent-overview-tab">Overview</span><Link to="/strategy" data-testid="agent-strategy-tab"><SlidersHorizontal size={14}/>Strategy</Link><Link to="/leaderboard" data-testid="agent-leaderboard-tab"><Trophy size={14}/>Contest</Link></div><div className="agent-page-grid"><div><AgentPanel agent={agent} onCreate={openCreate} onChange={update} large/>{agent&&<AgentTelemetry agent={agent}/>}</div><Journal events={events.filter(e=>e.agent_id===agent?.id)} agent={agent} expanded/></div><section className="collection-section"><div className="collection-heading"><div className="section-title"><Gem size={18}/><h2 data-testid="agent-collection-title">Your discoveries</h2></div><span className="neutral-badge" data-testid="agent-collection-count">{agent?.discoveries.length||0} / 3 discoveries</span></div><Collection agent={agent}/><p className="fine-print" data-testid="agent-collection-note">Collected underground. Independent of holder rewards.</p></section></div>}/>
 <Route path="/strategy" element={<StrategyPage key={identity.wallet?.wallet_id||'public'} agent={playableAgent} onCreate={openCreate} onSaved={refresh}/>}/>
 <Route path="/leaderboard" element={<ContestPage key={identity.wallet?.wallet_id||'public'} agent={playableAgent} onCreate={openCreate} onChange={update}/>}/>
 <Route path="/rewards" element={<Rewards/>}/><Route path="/guide" element={<Guide agent={agent}/>}/><Route path="*" element={<div className="not-found"><Compass size={40}/><h1 data-testid="not-found-title">An unmapped tunnel.</h1><p data-testid="not-found-description">This path leads back to the mine.</p><Link className="gold-button" data-testid="not-found-home" to="/">Back to the mine<ArrowRight size={16}/></Link></div>}/></Routes>
 <Footer online={!!world?.worker_online}/></main><AgentDialog open={create&&!!identity.wallet?.eligible} onClose={()=>setCreate(false)} onCreated={update}/><WalletDialog open={walletOpen} onClose={closeWallet}/><CrewDialog agent={selected?world?.agents.find(a=>a.id===selected.id)||selected:null} onClose={()=>setSelected(null)}/><Toaster theme="dark" position="bottom-right" toastOptions={{style:{background:'#1c1e21',border:'1px solid #393b3e',color:'#edede5',fontFamily:'DM Sans'}}}/></>;
}
export default function Main(){return <WalletProvider><BrowserRouter><Shell/></BrowserRouter></WalletProvider>;}