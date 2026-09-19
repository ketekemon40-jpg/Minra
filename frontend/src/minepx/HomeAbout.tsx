import {Link} from 'react-router-dom';
import {ArrowUpRight,ArrowDown} from 'lucide-react';
import './ProductUpdates.css';
export const HomeAbout=()=> <header className="home-about" data-testid="home-about">
 <div className="home-title-row"><div><div className="eyebrow" data-testid="mine-eyebrow"><span className="small-square"/>BRASS HOLLOW · SOLANA</div><h1 data-testid="mine-page-title">Minera<span>.</span></h1></div><span className="public-mine-marker" data-testid="public-view-status"><i className="status-dot"/>PUBLIC MINE</span></div>
 <p className="about-lead" data-testid="mine-page-subtitle">Hold Minera. Receive GLDX.</p>
 <div className="about-copy" data-testid="home-about-description"><p data-testid="home-about-project">Minera is an autonomous mining ecosystem on Solana. Independent agents bring its underground world to life, with GLDX rewards for eligible token holders.</p></div>
 <div className="about-links"><Link to="/rewards" className="text-button" data-testid="home-rewards-link">Holder rewards<ArrowUpRight size={14}/></Link><Link to="/guide" className="text-button" data-testid="home-guide-link">Explore the field guide<ArrowUpRight size={14}/></Link><a href="#underground" className="text-button about-mine-link" data-testid="home-enter-mine-link">Into the mine<ArrowDown size={14}/></a></div>
 </header>;