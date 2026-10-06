// Presentation bounds only; spring equations and integration methods are unchanged.
export const ENERGY_DURATION_S=12;
export const ENERGY_BATCH_STEPS=64;
export function energyStepLimit(dt){
  const count=ENERGY_DURATION_S/dt,rounded=Math.round(count);
  if(!Number.isFinite(count)||rounded<1||rounded>2400||Math.abs(count-rounded)>1e-9)
    throw new RangeError('Energy trajectory requires 1–2,400 whole fixed steps over 12 seconds');
  return rounded;
}
