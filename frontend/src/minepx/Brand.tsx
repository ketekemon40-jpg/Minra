import './Brand.css';

export const BrandMark=({placement}:{placement:'header'|'footer'})=> <img
 src={placement==='footer'?'/assets/branding/minera-icon-64.png':'/assets/branding/minera-logo.png'}
 className={`minera-mark minera-mark-${placement}`}
 alt={placement==='header'?'Minera logo':''}
 width={placement==='footer'?22:38}
 height={placement==='footer'?22:48}
 decoding="async"
 draggable={false}
 data-testid={`${placement}-brand-logo`}
/>;

export const BrandWordmark=()=> <span className="minera-lockup" data-testid="brand-wordmark">
 <b>Minera</b><small>AUTONOMOUS MINING</small>
</span>;