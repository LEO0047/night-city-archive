"""Acceptance against actual private evidence, public boundaries and stable IDs."""
import ast,collections,hashlib,json,pathlib,sqlite3,sys,urllib.request,wave
from phase2_index import ROOT,OUT
from phase2_rules import classify_record
PUBLIC=ROOT/'release/source' if (ROOT/'release/source/.git').exists() else ROOT

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name,passed,detail=None):
        checks.append(dict(name=name,passed=bool(passed),detail=detail));print(('PASS ' if passed else 'FAIL ')+name,flush=True)
    r=read(OUT/'rules.json');hold=read(ROOT/'reports/phase2/holdout.json');cat=read(ROOT/'web/catalogue.json');pub=read(PUBLIC/'docs/catalogue.json');mq=read(OUT/'mq027-private.json')
    check('rule_source_matches_output',r['rule_source_sha256']==digest(ROOT/'scripts/phase2_rules.py'))
    check('holdout_freezes_rule_output',hold['rules_sha256']==digest(OUT/'rules.json') and hold['fixture_sha256']==digest(ROOT/'research/phase2/user-fixtures.json'))
    fixture=read(ROOT/'research/phase2/user-fixtures.json');forbidden=[f.get('baseid','') for f in fixture['fixtures'] if f.get('baseid')]
    discovery_sources=['phase2_rules.py','phase2_index.py','phase2_context.py','phase2_operations.py','phase2_enrich.py']
    tainted={file:[word for word in forbidden+['user-fixtures','phase2_holdout','archived-conversation-titles'] if word.casefold() in (ROOT/'scripts'/file).read_text(encoding='utf-8').casefold()] for file in discovery_sources}
    check('discovery_does_not_import_holdout_or_fixture_ids',not any(tainted.values()),tainted)
    check('all_record_classifications_recomputed',all(classify_record(x['channels'],x['incoming'],x['asset_refs'])==(x['rule_status'],x['classification']) for x in r['records']),len(r['records']))
    check('quest_confidence_from_two_observations',all(q['classification']==('疑似刪除內容' if not q['flow_reached'] and q['missing_scenes'] else '證據不足') for q in r['quests']),len(r['quests']))
    controls=[x for x in hold['cases'] if x['fixture_id'].startswith('USER-C')]
    check('seven_active_controls_not_cut',len(controls)==7 and all(x['result']=='找到' and not x['false_positive'] for x in controls),[{k:x[k] for k in ('fixture_id','name','result')} for x in controls])
    check('holdout_reports_every_explicit_and_archived_case',len(hold['cases'])==len(fixture['fixtures'])+57,hold['counts'])
    q=mq['rule'];formal=[p for p in q['missing_scenes'] if 'mq027_' in pathlib.PureWindowsPath(p).name]
    check('mq027_independent_rule_and_six_formal_missing_scenes',q['classification']=='疑似刪除內容' and not q['flow_reached'] and len(formal)==6,formal)
    check('no_confirmed_unused_without_runtime_exclusion',all(f['classification']!='確認遊戲內未使用' for f in cat['findings']))
    check('unique_case_summaries_and_counterevidence',len({f['summary'] for f in cat['findings']})==len(cat['findings']) and len({tuple(f['counter']) for f in cat['findings']})==len(cat['findings']))
    check('classification_provenance_and_reproduction_visible',all(f['classification_origin'] in ('rule','analyst','community') and f['confidence_explanation'] and all(e['locator'] and e['command'] for e in f['evidence']) for f in cat['findings']))
    old=read(ROOT/'data/findings.json');oldids={f['id'] for f in old} if isinstance(old,list) else set()
    if not oldids:
        c=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);oldids={x[0] for x in c.execute('SELECT id FROM findings')};c.close()
    ids={f['id'] for f in cat['findings']};aliases=cat['aliases']
    check('all_34_old_ids_preserved_29_aliases',len(aliases)==29 and oldids<=ids|set(aliases) and all(v in ids for v in aliases.values()))
    records=[json.loads(x) for x in (ROOT/'exports/engram-findings-phase2.jsonl').read_text(encoding='utf-8').splitlines()];eng={r['id']:r for r in records}
    required={'schema','id','scan_id','title','category','classification','game','source_manifest_sha256','assets','interpretation','support','counterevidence','structural_evidence','sources','reproduce','reconstruction_status','canonical_status','local_only'}
    check('engram_v1_fields_and_redirects_preserved',oldids<=set(eng) and all(required<=set(r) and r['schema']=='nca.engram.finding/v1' for r in records) and all(eng[k]['superseded_by']==v for k,v in aliases.items()) and digest(ROOT/'exports/engram-findings.jsonl')==digest(ROOT/'exports/engram-findings-phase2.jsonl'),len(records))
    good=True
    for a in mq['audio']:
        p=ROOT/'data/media'/a['file'];good &= p.exists() and digest(p)==a['wav_sha256'] and bool(a['voice_map']) and a['transcription']['status']=='MACHINE_TRANSCRIPTION_UNREVIEWED'
        with wave.open(str(p)) as w:good &= w.getnframes()>0 and w.getframerate()>0
    check('145_audio_payloads_checksums_maps_and_asr_labels',len(mq['audio'])==145 and good,{'files':len(mq['audio']),'voice_ids':len(mq['voice_ids']),'seconds':round(sum(a['seconds'] for a in mq['audio']),4)})
    public_bytes=(PUBLIC/'docs/catalogue.json').read_text(encoding='utf-8')
    originals={x['female'] for x in mq['localization'] if len(x.get('female',''))>80}|{s['text'].strip() for a in mq['audio'] for s in a['transcription']['segments'] if len(s['text'].strip())>80}
    check('public_catalogue_excludes_private_long_text',not any(x in public_bytes for x in originals),{'private_strings_compared':len(originals)})
    sys.path.insert(0,str(PUBLIC/'scripts'));from check_public import validate_catalogue
    errors=validate_catalogue(pub);check('public_schema_and_payload_boundary',not errors,errors)
    requested=read(OUT/'resource-request.json')+read(OUT/'resource-extra-request.json');db=sqlite3.connect('file:'+str(OUT/'evidence.db').replace('\\','/')+'?mode=ro',uri=True)
    scanned=set(db.execute('SELECT archive,hash FROM resource_scan'));missing=[x for x in requested if (x['archive'],x['hash']) not in scanned];db.close()
    errors=[json.loads(x) for x in (OUT/'resource-scans-recovery/errors.jsonl').read_text().splitlines()];known={(x['archive'],x['hash']) for x in errors}
    check('world_decode_gaps_are_explicit',{(x['archive'],x['hash']) for x in missing}==known,{'requested':len(requested),'decoded':len(scanned),'unparsed':missing})
    coverage={'requested':len(requested),'decoded':len(scanned),'unparsed':missing,'errors':errors};(ROOT/'reports/phase2/resource-coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    before=read(ROOT/'reports/phase2/game-before.json');after=read(ROOT/'reports/phase2/game-after.json') if (ROOT/'reports/phase2/game-after.json').exists() else {}
    check('5151_original_game_files_unchanged',before.get('unchanged') and after.get('unchanged') and after.get('files')==5151,after)
    check('phase1_acceptance_still_passes',read(ROOT/'reports/acceptance.json').get('passed'))
    check('phase1_fresh_rebuild_matches',read(ROOT/'reports/rebuild.json').get('logical_match'))
    rebuild=read(ROOT/'reports/phase2/supplement-rebuild.json');check('phase2_fresh_rebuild_matches_all_tables',rebuild.get('status')=='passed' and rebuild.get('logical_match'))
    repro=read(ROOT/'reports/phase2/rule-repeat.json') if (ROOT/'reports/phase2/rule-repeat.json').exists() else {};check('rule_rerun_identical',repro.get('identical'),repro)
    used=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file());limit=read(ROOT/'config.json')['storage_limit_bytes'];check('within_approved_capacity',used<=limit,{'bytes':used,'limit':limit})
    report={'passed':all(c['passed'] for c in checks),'passed_checks':sum(c['passed'] for c in checks),'total_checks':len(checks),'checks':checks,'research_limit':'Technical checks passing does not validate community unobtainability claims.','holdout_counts':hold['counts']};(ROOT/'reports/phase2/acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
