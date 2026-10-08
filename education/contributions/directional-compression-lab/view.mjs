import {geometrySvg} from '../../web/property-labs.mjs';
import {BOX_FACES} from '../../web/continuum-properties.mjs';
export const sceneMarkup=state=>geometrySvg(state,BOX_FACES)
 .replace('Reference gray and prescribed blue geometry','Reference gray and solved passive blue geometry')
 .replace('Gray: reference. Blue: prescribed. SI readouts are unscaled.','Gray: reference. Blue: solved passive shape. SI readouts.');
