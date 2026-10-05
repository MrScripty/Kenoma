"""Check generated receipts, complete content, links, and PDF glyph/bounds sanity."""
from pathlib import Path
import gzip,hashlib,json,re
from urllib.parse import urlparse
import fitz
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'dist'
proof=json.loads((out/'proof-status.json').read_text())
assert proof['source_sha256']==hashlib.sha256((ROOT/'proofs/Mechanics.lean').read_bytes()).hexdigest()
assert proof['claims_sha256']==hashlib.sha256((ROOT/'proofs/claims.json').read_bytes()).hexdigest()
assert len(proof['claims'])==12 and all(c['status']=='checked' for c in proof['claims'])
assert all(set(c['axioms'])<={'propext','Quot.sound','Classical.choice'} for c in proof['claims'])
families=[(proof,'checked-source-appendix','proof-check-receipt','kernel-dependency-report')]
for receipt_name,source_name,claims_name,prefix,count in [('transfer-proof-status.json','AnatomicalTransfer.lean','anatomical-claims.json','transfer',2),('coupled-proof-status.json','CoupledMechanics.lean','coupled-claims.json','coupled',7),('arm-proof-status.json','AnatomicalArm.lean','arm-claims.json','arm',4),('property-proof-status.json','ContinuumProperties.lean','property-claims.json','property',8)]:
 receipt=json.loads((out/receipt_name).read_text())
 assert receipt['source_sha256']==hashlib.sha256((ROOT/'proofs'/source_name).read_bytes()).hexdigest()
 assert receipt['claims_sha256']==hashlib.sha256((ROOT/'proofs'/claims_name).read_bytes()).hexdigest()
 assert len(receipt['claims'])==count and all(c['status']=='checked' for c in receipt['claims'])
 assert all(set(c['axioms'])<={'propext','Quot.sound','Classical.choice'} for c in receipt['claims'])
 families.append((receipt,prefix+'-source-appendix',prefix+'-proof-receipt',prefix+'-kernel-report'))
total_claims=sum(len(r['claims']) for r,*_ in families)
scope=(ROOT/'book/chapters/00-scope.md').read_text()
assert f'The {total_claims} proof cards in this research edition' in scope,'Scope proof count differs from checked receipts'
properties=json.loads((out/'property-proof-status.json').read_text())
assert properties['mathlib']==json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
assert properties['mathlib']['commit']=='c44e0c8ee63ca166450922a373c7409c5d26b00b'
assert properties['source']=='proofs/ContinuumProperties.lean'
assert hashlib.sha256((out/'proofs/mathlib-lake-manifest.json').read_bytes()).hexdigest()==properties['mathlib']['manifest_sha256']
property_experiment=json.loads((out/'property-experiment.json').read_text())
for relative,digest in property_experiment['inputs'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Property experiment source changed: '+relative
assert abs(property_experiment['deformation']['volumeMeasurementDifference'])<1e-12
assert abs(property_experiment['isochoric']['volumeRatio']-1)<1e-12
assert abs(property_experiment['isochoric']['areaLengthMeasurementDifferenceM3'])<1e-15
active=property_experiment['activeTwoSegment']
assert abs(active['samples'][0]['strain']-1/300)<1e-12 and abs(active['samples'][1]['strain']+1/300)<1e-12
assert abs(active['numericalExtensionM'])<1e-14
errors=[abs(row['extensionErrorM']) for row in property_experiment['taperRefinement']]
assert all(errors[i]<errors[i-1]/3.8 for i in range(1,len(errors)))
property_browser=json.loads((out/'qa/property-browser-check.json').read_text())
assert property_browser['result']=='PASS_INTEGRATED_PROPERTY_LABS' and property_browser['proof_cards']==total_claims
assert property_browser['html_sha256']==hashlib.sha256((out/'index.html').read_bytes()).hexdigest()
assert property_browser['app_sha256']==hashlib.sha256((out/'assets/app.js').read_bytes()).hexdigest()
assert property_browser['manifest_sha256']==hashlib.sha256((out/'build-manifest.json').read_bytes()).hexdigest()
warning_audit=json.loads((out/'data/property-labs-v1/endpoint-warning-audit.json').read_text())
assert warning_audit['result']=='PASS_PRESERVED_WARNING_FAILURE_AND_ENDPOINT_CORRECTION'
assert not warning_audit['frozen']['smallStrainWarning'] and warning_audit['corrected']['smallStrainWarning']
assert abs(warning_audit['oracleMaximumStrain']-3/55)<1e-15
assert all(r['smallStrainWarning'] and abs(r['trueMaximumStrain']-3/55)<1e-15 for r in warning_audit['refinements'])
for relative,digest in warning_audit['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Endpoint audit source changed: '+relative
property_render=json.loads((out/'property-book-review/render-receipt.json').read_text())
assert property_render['result']=='PASS_PROPERTY_BOOK_RENDER_CAPTURE'
assert property_render['html_sha256']==hashlib.sha256((out/'index.html').read_bytes()).hexdigest()
assert property_render['pdf_sha256']==hashlib.sha256((out/'kenoma-mechanics.pdf').read_bytes()).hexdigest()
assert property_render['build_manifest_sha256']==hashlib.sha256((out/'build-manifest.json').read_bytes()).hexdigest()
assert property_render['inspector_sha256']==hashlib.sha256((ROOT/'tools/inspect_property_integration.py').read_bytes()).hexdigest()
assert all(not v['horizontalOverflow'] and v['proofCards']==total_claims for v in property_render['views'])
assert not property_render['page_errors']
for name,digest in property_render['outputs'].items():
 assert hashlib.sha256((out/'property-book-review'/name).read_bytes()).hexdigest()==digest,'Property render changed: '+name
compression=json.loads((out/'compression-experiment.json').read_text())
assert compression['result']=='PASS_LAB5_COMPRESSION_EXPERIMENT'
assert compression==json.loads((ROOT/'data/compression-lab-v1/benchmark.json').read_text())
for relative,digest in compression['inputs'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Compression source differs: '+relative
assert all(s['accepted'] and s['J']>0 and abs(s['volumeMeasurementDifference'])<1e-12 and abs(s['volumeEquilibriumDifference'])<1e-10 for s in compression['rows'])
assert all(abs(s['forceResidualN'])<=1e-8 for s in compression['forceControlled'])
assert all(not c['accepted'] and not c['stateAdvanced'] for c in compression['negativeCases'])
compression_browser=json.loads((out/'qa/compression-browser-check.json').read_text())
assert compression_browser['result']=='PASS_LAB5_COMPRESSION_BROWSER' and not compression_browser['javascript_errors']
assert compression_browser['html_sha256']==hashlib.sha256((out/'index.html').read_bytes()).hexdigest()
assert compression_browser['manifest_sha256']==hashlib.sha256((out/'build-manifest.json').read_bytes()).hexdigest()
compression_render=json.loads((out/'compression-book-review/render-receipt.json').read_text())
assert compression_render['result']=='PASS_COMPRESSION_BOOK_RENDER_CAPTURE'
assert compression_render['pdf_sha256']==hashlib.sha256((out/'kenoma-mechanics.pdf').read_bytes()).hexdigest()
assert compression_render['html_sha256']==compression_browser['html_sha256']
assert compression_render['inspector_sha256']==hashlib.sha256((ROOT/'tools/inspect_compression_integration.py').read_bytes()).hexdigest()
assert all(not v['horizontalOverflow'] and v['proofCards']==total_claims for v in compression_render['views'])
for name,digest in compression_render['outputs'].items():
 assert hashlib.sha256((out/'compression-book-review'/name).read_bytes()).hexdigest()==digest
audit='data/anatomical-arm-v1/audit/'
for stem,status,steps in [('contact-lift-release','PASS',15),('contact-fine-release','PASS_ACCEPTED_PREFIX',22)]:
 receipt=json.loads((out/audit/(stem+'-recheck.json')).read_text())
 execution=out/audit/(stem+'-results.json')
 assert receipt['result']==status and receipt['verifiedSteps']==steps
 assert receipt['executionReceiptSHA256']==hashlib.sha256(execution.read_bytes()).hexdigest()
 verifier='tools/verify-anatomical-contact-trajectory.mjs' if stem=='contact-lift-release' else 'tools/verify-anatomical-release-prefix.mjs'
 assert receipt['verifierSHA256']==hashlib.sha256((ROOT/verifier).read_bytes()).hexdigest()
 for relative,digest in receipt['executionSourceHashes'].items():
  assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Trajectory source changed: '+relative
 assert all(r['transverseCrossingPairs']==0 and r['tendonViolations']==0 and r['residualN']<=1e-4 for r in receipt['rows'])
 assert json.loads(execution.read_text())['completedAllSteps']==(stem=='contact-lift-release')
compression=json.loads((out/audit/'anatomical-compression-sensitivity.json').read_text())
assert compression['result']=='COMPLETED_FROZEN_POSE_DIAGNOSTIC'
assert compression['unchangedStationarityToleranceN']==1e-4
assert len(compression['states'])==16 and len(compression['selectedResults'])==5
assert compression['executionReceiptSHA256']==hashlib.sha256((out/audit/'contact-lift-release-results.json').read_bytes()).hexdigest()
assert compression['acceptedReplaySHA256']==hashlib.sha256((out/audit/'contact-lift-release-recheck.json').read_bytes()).hexdigest()
for relative,digest in compression['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Compression diagnostic source changed: '+relative
dense=json.loads((out/audit/'anatomical-dense-step-recheck.json').read_text())
dense_execution=json.loads((out/audit/'anatomical-dense-step.json').read_text())
assert dense['result']=='PASS_ACCEPTED_COMPARISON'
assert dense['unchangedStationarityToleranceN']==1e-4
assert dense['residualN']<=1e-4 and dense['independentResidualN']<=1e-4
assert dense['surfaceAudit']['transverseCrossingPairs']==0 and dense['routingAudit']['accepted']
assert all(v==0 for v in dense['sampledPenetrationsM'].values())
assert dense['executionReceiptSHA256']==hashlib.sha256((out/audit/'anatomical-dense-step.json').read_bytes()).hexdigest()
assert dense['verifierSHA256']==hashlib.sha256((ROOT/'tools/verify-anatomical-dense-step.mjs').read_bytes()).hexdigest()
assert dense_execution['accepted'] and dense_execution['pointsPerElement']==256
for relative,digest in dense_execution['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Dense comparison source changed: '+relative
trajectory=json.loads((out/audit/'anatomical-dense-trajectory-recheck.json').read_text())
trajectory_execution=json.loads((out/audit/'anatomical-dense-trajectory.json').read_text())
assert trajectory['result']=='PASS_DENSE_TRAJECTORY' and trajectory['verifiedSteps']==15
assert trajectory_execution['result']=='ACCEPTED_DENSE_TRAJECTORY' and trajectory_execution['completedAllSteps']
assert trajectory['executionReceiptSHA256']==hashlib.sha256((out/audit/'anatomical-dense-trajectory.json').read_bytes()).hexdigest()
assert trajectory['verifierSHA256']==hashlib.sha256((ROOT/'tools/verify-anatomical-dense-trajectory.mjs').read_bytes()).hexdigest()
assert all(r['independentResidualN']<=1e-4 and r['minimumCornerJ']>1e-6 and r['surfaceAudit']['transverseCrossingPairs']==0 and r['routingAudit']['accepted'] and all(v==0 for v in r['sampledPenetrationsM'].values()) for r in trajectory['rows'])
assert abs(trajectory['rows'][-1]['timeS']-.43)<1e-12
assert trajectory['behavior']['releaseFallFromPeakRad']>0 and trajectory['behavior']['finalVelocityRadPerS']<0
for name in ['anatomical-dense-trajectory.json','anatomical-enriched-step.json','anatomical-fixed-end-compression.json','anatomical-further-integration.json','anatomical-nodal-probe.json','anatomical-compression-localization.json','anatomical-calibration-geometry.json','anatomical-nodal-force-components.json']:
 receipt=json.loads((out/audit/name).read_text())
 for relative,digest in receipt['sourceHashes'].items():
  assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Dense qualification source changed: '+relative
enriched=json.loads((out/audit/'anatomical-enriched-step-recheck.json').read_text())
assert enriched['result']=='PASS_ACCEPTED_ENRICHED_COMPARISON' and enriched['independentResidualN']<=1e-4
assert enriched['executionReceiptSHA256']==hashlib.sha256((out/audit/'anatomical-enriched-step.json').read_bytes()).hexdigest()
assert enriched['verifierSHA256']==hashlib.sha256((ROOT/'tools/anatomical-enriched-step.mjs').read_bytes()).hexdigest()
assert len(enriched['additionalCoordinatesM'])==6 and next(h for h in enriched['heads'] if h['elementId']=='FJ1512')['coordinateCount']==69
plot_path='data/anatomical-arm-v1/review/dense-qualification/coarse/'
plot=json.loads((out/plot_path/'render-receipt.json').read_text())
assert plot['rendererSHA256']==hashlib.sha256((ROOT/'tools/dense_qualification_figure.py').read_bytes()).hexdigest()
for relative,digest in plot['inputs'].items():
 assert hashlib.sha256((out/'data/anatomical-arm-v1'/relative).read_bytes()).hexdigest()==digest,'Stale plotted input: '+relative
for relative,digest in plot['outputs'].items():
 assert hashlib.sha256((out/plot_path/relative).read_bytes()).hexdigest()==digest,'Changed qualification figure: '+relative
orientation=json.loads((out/audit/'anatomical-trajectory-orientation-summary.json').read_text())
archive=(out/audit/orientation['archive']).read_bytes();decoded=gzip.decompress(archive)
assert orientation['result']=='PASS_EXACT_STORED_P2_ORIENTATION' and orientation['certifiedElementCount']==29988
assert hashlib.sha256(archive).hexdigest()==orientation['archiveSHA256']
assert hashlib.sha256(decoded).hexdigest()==orientation['fullReceiptSHA256']
full_orientation=json.loads(decoded)
assert sum(h['elementCount'] for r in full_orientation['rows'] for h in r['heads'])==29988
assert all(e['orientationCertified'] and all(len(e[k]['coefficients'])==20 and all(int(c['numerator'])>0 for c in e[k]['coefficients']) for k in ['reference','current']) for r in full_orientation['rows'] for h in r['heads'] for e in h['elements'])
for relative,digest in orientation['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Orientation certificate source changed: '+relative
envelope_path='data/anatomical-arm-v1/review/dense-qualification/envelope/'
envelope_plot=json.loads((out/envelope_path/'render-receipt.json').read_text())
envelope_bytes=(out/audit/'anatomical-dense-envelope.json').read_bytes()
assert envelope_plot['inputSHA256']==hashlib.sha256(envelope_bytes).hexdigest()
assert envelope_plot['rendererSHA256']==hashlib.sha256((ROOT/'tools/dense_envelope_figure.py').read_bytes()).hexdigest()
for relative,digest in json.loads(envelope_bytes)['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Envelope export source changed: '+relative
for relative,digest in envelope_plot['outputs'].items():
 assert hashlib.sha256((out/envelope_path/relative).read_bytes()).hexdigest()==digest,'Changed envelope render: '+relative
text=(out/'kenoma-mechanics.md').read_text();assert not re.search(r'\{\{[A-Za-z]',text)
assert f'The {total_claims} proof cards in this research edition' in text,'Manuscript proof count differs from checked receipts'
for id in ['force-pair','torque-linearity','torque-origin','central-pair','kinetic-sign','torque-example','volume-edge-translation','volume-det-compose','volume-diagonal','volume-isochoric-sqrt']:
 assert f'Checked claim {id}:' in text
browser=json.loads((out/'browser-check.json').read_text());assert browser['status']=='passed'
assert browser['proof_cards']==total_claims
assert browser['html_sha256']==hashlib.sha256((out/'index.html').read_bytes()).hexdigest()
assert browser['app_sha256']==hashlib.sha256((out/'assets/app.js').read_bytes()).hexdigest()
mobile=json.loads((out/'mobile-startup-check.json').read_text())
assert mobile['status']=='passed' and mobile['downloads_on_start']==[]
assert mobile['html_sha256']==browser['html_sha256'] and mobile['app_sha256']==browser['app_sha256']
assert set(mobile['startup_draws'])=={'force','torque','energy','elbow','series','continuum','spatial','atlas'}
assert all(d['available'] and not d['lost'] and d['unique_colors']>100 and d['vivid_geometry_pixels']>300 for d in mobile['startup_draws'].values())
doc=fitz.open(out/'kenoma-mechanics.pdf');combined='\n'.join(page.get_text() for page in doc)
assert len(doc)>5 and '\ufffd' not in combined
for needle in ['Force changes motion','Energy reveals numerical error','Checked source appendix','14.715','0.80','Store tendon energy','Inspect real anatomy','4,403','51.243524','798.52','Measure deformation','Volume and cross-section','Uneven axial strain']:
 assert needle in combined,needle
spatial=json.loads((out/'spatial-experiment.json').read_text());reference=spatial['reference']
assert spatial['sourceSha256']==hashlib.sha256((ROOT/'web/spatial.mjs').read_bytes()).hexdigest()
assert f"{reference['penetrationM']*1000:.4f} mm" in (out/'assets/spatial.svg').read_text()
assert f"Maximum free-force defect is {reference['maxFreeForceN']:.6f} N" in text
manifest=json.loads((out/'build-manifest.json').read_text())
for relative,digest in manifest['input_sha256'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Build input changed: '+relative
for item in json.loads((out/'data/elbow-v1/provenance.json').read_text())['files']:
 assert hashlib.sha256((out/'data/elbow-v1'/item['path']).read_bytes()).hexdigest()==item['sha256']
proof_destinations={key:0 for _,*keys in families for key in keys}
for page in doc:
 for link in page.get_links():
  uri=link.get('uri','');parsed=urlparse(uri)
  assert parsed.hostname not in {'127.0.0.1','localhost','::1'} and parsed.scheme!='file',f'Nonportable PDF link: {uri}'
  destination=link.get('nameddest')
  if destination in proof_destinations:
   assert 0<=link.get('page',-1)<len(doc),'Unresolved internal PDF proof destination'
   proof_destinations[destination]+=1
 for block in page.get_text('blocks'):
  assert block[0]>=-1 and block[1]>=-1 and block[2]<=page.rect.width+1 and block[3]<=page.rect.height+1
assert all(proof_destinations[key]==len(receipt['claims']) for receipt,*keys in families for key in keys),'Missing internal PDF proof destinations'
spans=[span for page in doc for block in page.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
print_label_sizes={}
for label in ['Humerus','Triceps medial head','Unit 1','Elapsed time from retained trial segment (s)']:
 sizes=[s['size'] for s in spans if s['text']==label]
 assert sizes and min(sizes)>=10,'Evidence figure label is missing or too small: '+label
 print_label_sizes[label]=round(min(sizes),2)
results={'status':'passed','pdf_pages':len(doc),'proof_cards':total_claims,'pdf_links':'no loopback or file URLs','pdf_proof_destinations':proof_destinations,'browser':browser['browser_version'],
 'print_figure_label_minimum_pt':print_label_sizes,
 'scope':'Content, hash, glyph and page-bounds sanity; PDF appearance still requires visual review.'}
(out/'artifact-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
