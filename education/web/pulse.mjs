// A pulse is an input schedule on the current state, never an initialization.
export function currentPulse(time, excitation){
 if(!Number.isFinite(time)||time<0||!Number.isFinite(excitation)||excitation<0||excitation>1)throw new Error('Invalid pulse state/input');
 return {startTime:time,releaseTime:time+.3,excitation};
}
export const pulseDue=(pulse,time)=>Boolean(pulse&&time>=pulse.releaseTime-1e-12);
