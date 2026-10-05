"""Static and interactive prescribed-kinematics blocks from one specification."""
import html
SPECS={
 'deformation':('Property lab 1 · Measure deformation',[
 ('sx','Axial stretch',.4,1.7,.01,1.2),('sy','Y stretch',.4,1.7,.01,.85),('sz','Z stretch',.4,1.7,.01,1.03),('shear','Simple shear',-.8,.8,.01,.25),('angle','Rotation (degrees)',-180,180,1,20),('tx','Translation X (mm)',-50,50,1,0),('ty','Translation Y (mm)',-50,50,1,0),('tz','Translation Z (mm)',-50,50,1,0)]),
 'tapered':('Property lab 3 · Uneven axial strain',[('length','Reference length (m)',.05,.5,.01,.2),('area','Narrow area (m²)',.0001,.001,.0001,.0003),('ratio','End area ratio',.5,4,.1,2),('modulus','Modulus E (Pa)',50000,500000,10000,100000),('force','Passive tensile force (N)',-1,1,.1,.3),('activeStress','Active stress offset (Pa)',0,2000,100,1000),('activation','Activation fraction',0,1,.05,1)]),
 'isochoric':('Property lab 2 · Volume and cross-section',[
 ('axial','Axial stretch',.4,1.7,.01,.8),('lateral','Independent lateral stretch',.4,1.7,.01,1)])}
def block(key,web):
 title,controls=SPECS[key]
 caption='Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.'
 if key=='tapered':caption='Small-strain constant-modulus bar; no distributed axial load. Strain by axial position, with blue extension and red compression. Area controls an axial resultant, not a complete muscle law.'
 if not web:return f'\n### {title}\n\n![{caption}](assets/property-{key}.svg)\n\n{caption}\n\n[Open the interactive lesson](index.html#lab-property-{key}).\n'
 fields=''
 for param,label,low,high,step,value in controls:
  fields+=f'<div class="control"><label for="property-{key}-{param}">{label}</label><div class="input-pair"><input type="range" aria-label="{label} slider" data-param="{param}" min="{low}" max="{high}" step="{step}" value="{value}"><input id="property-{key}-{param}" type="number" data-param="{param}" min="{low}" max="{high}" step="{step}" value="{value}"></div></div>'
 if key=='isochoric':fields+='<div class="control"><label for="property-iso-mode">Stretch relation</label><select id="property-iso-mode" data-param="mode"><option value="isochoric">Isochoric: b = 1 / sqrt(axial)</option><option value="independent">Independent stretches</option></select></div>'
 if key=='tapered':
  for param,label,options in [('mode','Boundary / load condition',[('passive','Prescribed passive force'),('active-fixed','Uniform active stress; fixed ends')]),('shape','Area profile',[('linear','Linear area taper'),('two-segment','Two equal-length segments')]),('segments','Midpoint cells',[(8,'8'),(16,'16'),(32,'32'),(64,'64'),(128,'128')])]:
   fields+=f'<div class="control"><label for="property-tapered-{param}">{label}</label><select id="property-tapered-{param}" data-param="{param}">'+''.join(f'<option value="{v}"'+(' selected' if v==16 else '')+f'>{text}</option>' for v,text in options)+'</select></div>'
 invert='<button type="button" data-action="invert">Try inverted candidate</button>' if key=='deformation' else ''
 return f'''\n<section class="laboratory property-lesson" data-property="{key}" id="lab-property-{key}" aria-labelledby="property-{key}-heading"><h3 id="property-{key}-heading">{title}</h3><p class="model-label">Declared reduced fixture; SI units; scope and assumptions in the adjacent derivation.</p><figure class="static-figure"><img src="assets/property-{key}.svg" alt="{html.escape(caption)}"><figcaption>{caption}</figcaption></figure><div class="property-scene"></div><p>{caption}</p><div class="controls">{fields}</div><div class="actions"><button type="button" data-action="reset">Reset</button>{invert}<button type="button" data-action="summary">Read current results</button><button type="button" data-action="copy">Copy state</button></div><dl class="readout" aria-label="Measured kinematics"></dl><p class="announce" role="status" aria-live="polite"></p><textarea class="preset" aria-label="Reproducible kinematics JSON" readonly hidden></textarea><noscript>Interactive controls require JavaScript. The static illustration and equations remain available.</noscript></section>\n'''
