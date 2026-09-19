import {useEffect,useState} from 'react';
import {Pickaxe,BookOpen} from 'lucide-react';
import {Dialog,DialogContent,DialogTitle,DialogDescription} from '../components/ui/dialog';
import {Agent,JournalEvent,stageNames} from './types';
import {Avatar} from './Avatar';
import {request} from './api';
export const CrewDialog=({agent,onClose}:{agent:Agent|null;onClose:()=>void})=>{
 const [events,setEvents]=useState<JournalEvent[]>([]),[error,setError]=useState('');
 const agentId=agent?.id,agentStep=agent?.step;
 useEffect(()=>{setEvents([]);setError('');if(!agentId)return;let live=true;request<JournalEvent[]>(`/journal?agent_id=${agentId}&limit=4`).then(d=>{if(live)setEvents(d);}).catch(()=>{if(live)setError('Field reports could not be loaded.');});return()=>{live=false;};},[agentId,agentStep]);
 return <Dialog open={!!agent} onOpenChange={v=>{if(!v)onClose();}}><DialogContent className="mine-dialog crew-dialog" data-testid="crew-details-dialog">{agent&&<>
 <div className="crew-dialog-profile"><Avatar avatar={agent.avatar} size={95}/><div><span className="bot-tag" data-testid="crew-details-type">{agent.is_bot?'RESIDENT AGENT':'WALLET AGENT'}</span><DialogTitle data-testid="crew-details-name">{agent.name}</DialogTitle><DialogDescription data-testid="crew-details-personality">{agent.personality} · Brass Hollow</DialogDescription></div></div>
 <div className="agent-task" data-testid="crew-details-stage"><Pickaxe size={15}/>{agent.status==='active'?stageNames[agent.stage]:agent.status==='paused'?'Resting':'At basecamp'}</div><div className="agent-stats"><div><span>Ore collected</span><strong data-testid="crew-details-ore">{agent.ore}</strong></div><div><span>Expeditions</span><strong data-testid="crew-details-expeditions">{agent.expeditions}</strong></div></div>
 <div className="section-title"><BookOpen size={15}/><h2 data-testid="crew-reports-title">Latest field reports</h2></div>{error&&<p className="form-error" data-testid="crew-journal-error">{error}</p>}{events.map(e=><div className="crew-report" key={e.id} data-testid={`crew-report-${e.id}`}><p>“{e.message}”</p><time>{new Date(e.created_at).toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit'})}</time></div>)}{!events.length&&!error&&<p data-testid="crew-reports-empty">No field reports yet.</p>}{agent.is_bot&&<p className="access-note" data-testid="crew-financial-note">An autonomous resident of Brass Hollow. Resident agents do not enter contests or receive holder rewards.</p>}
 </>}</DialogContent></Dialog>;
};