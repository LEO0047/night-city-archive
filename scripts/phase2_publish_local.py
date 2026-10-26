"""Build the reviewable local/private and public-text editions. Never git push.

Interpretation authored here is explicitly analyst provenance. All rule results
are imported unchanged from phase2_rules.py; fixtures cannot promote findings.
"""
import collections,hashlib,json,pathlib,shutil,sqlite3
from phase2_index import ROOT,OUT
PUBLIC=ROOT/'release/source' if (ROOT/'release/source/.git').exists() else ROOT

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def ident(slug):return 'NCA-'+hashlib.sha256(slug.encode()).hexdigest()[:12].upper()
def evidence(i,label,observation,locator,command):return dict(id=i,label=label,observation=observation,locator=locator,command=command)
def section(heading,*paragraphs,evidence_ids=None):return dict(heading=heading,paragraphs=list(paragraphs),evidence_ids=evidence_ids or [])

def main():
    core=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);core.row_factory=sqlite3.Row
    rules=read(OUT/'rules.json');mq=read(OUT/'mq027-private.json');holdout=read(ROOT/'reports/phase2/holdout.json');sources=read(ROOT/'research/phase2/sources.json')
    operations=read(OUT/'quest-operations.json');config=read(ROOT/'config.json');old=[dict(r) for r in core.execute('SELECT * FROM findings ORDER BY id')]
    def assets(hashes):
        result=[]
        for h in sorted(set(hashes)):
            r=core.execute('SELECT hash,path,extension FROM assets WHERE hash=?',(h,)).fetchone()
            if not r:continue
            a=dict(r);a['archives']=[dict(r) for r in core.execute('SELECT a.path,a.sha256,e.sha1 entry_sha1 FROM entries e JOIN archives a ON a.id=e.archive_id WHERE e.hash=? ORDER BY a.path',(h,))];result.append(a)
        return result
    def make(i,title,summary,categories,classification='證據不足',origin='analyst'):
        return dict(id=i,title=title,summary=summary,categories=categories,classification=classification,classification_origin=origin,community='未核定新穎性',system_conclusion='',analyst_conclusion='',community_note='未把社群標籤作為規則輸入。',sections=[],support=[],counter=[],evidence=[],confidence_explanation='',assets=[],sources=[],next_test='')
    mqf=make('NCA-AB6DD4DA3FB3','MQ027 / Living on the Edge','新聞團隊、危險特技與失去工作的駕駛：192 個資產保留故事，但正式場景缺件，現行任務入口未連通。',['任務與對白','角色','車輛'],mq['rule']['classification'],'rule')
    mqf.update(community='歷史線索；本版重新查證',system_conclusion=f"{mq['rule']['rule_status']}：正式流程可達 {len(mq['rule']['flow_reached'])} 個核心資源；{len(mq['rule']['missing_scenes'])} 條場景路徑沒有對應資產。",analyst_conclusion='目前版本的 MQ027 特技任務流程殘缺且不接正式流程，支持「疑似刪除內容」。尚不足以聲稱這組所有角色、共用模型、世界標記或錄音都完全未使用。',community_note='歷史討論提到早期版本差異，但本次未取得舊版，也未讀到全文；不採用確切移除版本作為結論。',flow=['N54 拍攝團隊','駕駛受傷／V 接替','錄影與機車特技','報酬／名氣分支','Jessy 與 Stan 的後續訊息'])
    mqf['sections']=[
      section('一份缺了正式場景的特技任務','原始日誌標題鍵 LocKey#10390 對應 Living on the Edge。日誌、角色定義、錄音與任務節點共同描述：V 遇到 N54 新聞團隊，在原駕駛出事後接替特技工作。這是本機內容的研究重述，並非已恢復可玩的任務。','現存 6 個 questphase、1 個 quest、1 個獨立 gamedef，以及 2 個 chickentest 場景。主階段頂層有 28 個節點；其他巢狀圖、訊息與收尾階段也保留。',evidence_ids=['MQ-01','MQ-02']),
      section('角色與關係','Character.mq027_director 的顯示名稱為 Jessy；原始文字鍵還給出 Jessica Yu。Character.mq027_driver 為 Suicide Stan／Stanley Carlson；Character.mq027_recorder 為 Kikil／Kikil Ivakin。角色名稱取自 TweakDB 與本機文字，沒有採信機器轉錄對人名的猜測。','Jessy 負責拍攝與報酬，Stan 是被 V 接替的駕駛，Kikil 是團隊成員。角色用途來自記錄名稱、文字與語音的交叉判讀；模型目前是代理外觀，不代表最終人物造型。',evidence_ids=['MQ-03','MQ-04']),
      section('原本要玩到什麼','原始日誌與指令保留裝上錄影設備、騎機車進入 AV、沿建築／檢查點完成限時特技等步驟。可見的分支涉及報酬與名氣，以及是否替 Stan 支付醫療費。','後續訊息分支包括 Jessy 告知影片成果、機車禮物，以及 Stan 對工作被搶走的不滿或對醫療協助的感謝。這證明作者寫過這些後續，不證明目前能觸發獎勵。逐段原始日誌只在私人聽讀室顯示。',evidence_ids=['MQ-01','MQ-05']),
      section('原本可能接在哪裡','獨立 gamedef 使用夜城的 streamingworld，出生標記為 mq027_spwn_kiroshi；社群與節點參照另有 Arroyo、downhill 等線索。因此可提出與 Kiroshi／Arroyo 周邊特技路線相關的假說。','本次沒有把這些標籤解算成經遊戲驗證的座標，也沒有證明上市版曾在該處出現任務入口。確切街口與觸發時機仍待世界節點定位。',evidence_ids=['MQ-02','MQ-06']),
      section('現在為什麼走不到','從本體與 EP1 兩個正式 gamedef 出發，沿 gamedef／quest／questphase／scene 引用，沒有到達 MQ027 的正式流程。主階段仍指向 mq027_01_stunt_00、03_stunt_02、04_stunt_03、05_stunt_04、06_owstunt01、07_owstunt02 六個 scene；目前全資產索引均找不到這些精確路徑。','第七條缺失引用指向 scenes\\mq025_00_chickentest.scene。同名檔只存在 test 與 test\\versions\\gold，這是路徑不符；不能用兩份測試場景宣稱已找回六個正式場景。','以上是結構性的中斷證據。它不等同於執行所有存檔狀態後證明整組資產永遠不會載入。',evidence_ids=['MQ-02','MQ-07']),
      section('能聽到多少，不能聽出什麼',f"保留 {len(mq['audio'])} 個英文語音檔，合計約 {sum(a['seconds'] for a in mq['audio'])/60:.2f} 分鐘，映射到 {len(mq['voice_ids'])} 個 voice string ID。每段附 WEM 路徑、封存檔、voiceovermap 的 JSON 指標與轉換後 WAV 校驗值。",'搜尋 en-us 與 zh-tw 字幕索引沒有找到這 117 個 ID 的字幕。私人版提供原音與離線機器轉錄；轉錄標記為未校對，不能冒充遊戲原始字幕。',evidence_ids=['MQ-04']),
    ]
    mqf['support']=['兩個正式流程入口皆未連到 MQ027；判定不是由 mq027 檔名或社群標籤觸發。','主階段明確引用六個缺失正式場景；全 553,470 個資產查詢均未命中精確路徑。','角色、日誌、後續訊息與 145 段錄音互相補足，足以重建設計故事。']
    mqf['counter']=['Johnny 的 mq027_ws_johnny_final／stunt 標記仍出現在 always_loaded 世界資料；某些共用部分可能仍被載入。','Vehicle.mq027_news_av 指向共用 av_zetatech_atlus_basic_01.ent；不能把整台 AV 模型說成廢棄載具。','test 與 gold 資料夾有兩份 chickentest；測試場景的存在削弱「整組完全被刪除」說法，但沒有補上正式場景。','沒有舊版本比對，無法確認何時移除，也不能把歷史 prophet 的稱呼直接當作本次 stunts 流程。']
    mqf['evidence']=[
      evidence('MQ-01','原始日誌','任務標題、目標與分支訊息的原始定位。','quests/minor_quest/mq027_stunts; contacts/jessy; LocKey#10390','python -X utf8 scripts/phase2_query.py --sql "SELECT hash,archive_id,pointer,path,type FROM journal_nodes WHERE path LIKE \'%mq027%\'"'),
      evidence('MQ-02','任務與獨立入口','gamedef、主階段與獨立測試入口。','base\\quest\\minor_quests\\mq027\\mq027.gamedef; mq027.questphase','python -X utf8 scripts/phase2_query.py --quest mq027'),
      evidence('MQ-03','角色與新聞 AV','5 個相關記錄；名稱與實體資源可重查。','Character.mq027_director / driver / recorder; Vehicle.mq027_news_av','python -X utf8 scripts/phase2_query.py --record Character.mq027_director\npython -X utf8 scripts/phase2_query.py --record Vehicle.mq027_news_av'),
      evidence('MQ-04','原音及映射','145 段 WAV 的來源與轉錄 provenance；完整內容只在私人版。','data/phase2/audio/inventory.json; *.asr.json; base\\localization\\en-us\\voiceovermap.json','python -X utf8 scripts/phase2_audio.py\npython -X utf8 scripts/phase2_mq027.py'),
      evidence('MQ-05','收尾分支',' finished 與 msg_return 圖保留後續訊息節點。','base\\quest\\minor_quests\\mq027\\phases\\mq027_finished.questphase; mq027_msg_return.questphase','python -X utf8 scripts/phase2_mq027.py'),
      evidence('MQ-06','世界殘留與具體反證',f"世界／實體索引中有 {len(mq['world_matches'])} 個相關欄位見證；完整集合留在私人證據庫。",'base\\worlds\\03_night_city\\_compiled\\default\\always_loaded_1.streamingsector','python -X utf8 scripts/phase2_query.py --sql "SELECT hash,archive,pointer,value FROM resource_fields WHERE lower(value) LIKE \'%mq027%\'"'),
      evidence('MQ-07','精確缺件表','每條缺失引用都列出來源階段與欄位，無同名替代推論。','\n'.join(mq['rule']['missing_scenes']),'python -X utf8 scripts/phase2_query.py --quest mq027')]
    mqf['confidence_explanation']='規則採可重算條件：沒有正式流程入口 AND 有缺失場景 payload => 疑似刪除內容。這兩條均來自索引；沒有手寫分數。確認未使用還需要排除動態／原生／存檔入口，因此不升到最高級。'
    mqf['assets']=[{k:a[k] for k in ('hash','path','extension','archives')} for a in mq['assets']];mqf['sources']=['S-WKIT','S-TWEAKS','S-MQ027-HISTORY'];mqf['next_test']='先解算 Kiroshi／Arroyo 的世界節點座標及正式觸發條件。若需要舊版做版本差異，另附容量與取得方式請求授權。'
    findings=[mqf]
    # Merge presentation only; old findings remain immutable historical records.
    dev=[r for r in old if r['confidence']=='測試或開發殘留'];aliases={r['id']:ident('dev-backstage-overview') for r in dev}
    f=make(ident('dev-backstage-overview'),'開發者後台總覽 / 29 個歷史入口','把分散的測試入口收成一張開發工作台地圖；舊連結仍可定位原來的內容群。',['開發者後台'],'測試或開發殘留')
    f.update(system_conclusion='沿用第一階段結構候選，沒有把 29 組各自計作新發現。',analyst_conclusion='獨立啟動入口、測試流程與場景搭配支持開發用途；沒有推論所有相依模型未使用。',community_note='這是研究整理分類，不宣稱 29 個新廢案。',aliases=[{'id':r['id'],'title':r['title']} for r in dev])
    f['sections']=[section('如何閱讀後台','每個舊 ID 轉到此總覽。原始候選成員仍保留在第一階段索引，ENGRAM 匯出保留同一 ID 並新增 superseded_by。名稱中的 test 只幫助定位，實際判讀還要求可解析的獨立入口與其任務／場景關係。')]
    f['support']=[f'{len(dev)} 組歷史入口可逐一查回成員、來源 archive 和結構引用。','合併只改展示層，不重用舊識別碼。'];f['counter']=['後台入口引用的共用動畫、角色或材質可能同時服務正式任務；合併不改變其個別使用狀態。','部分測試流程未完整解析所有外部觸發，不能由後台位置推出玩家絕不會碰到相依資產。']
    f['evidence']=[evidence('DEV-01','原始群組與轉址','29 個舊 ID 對一個穩定總覽 ID。','exports/phase2-aliases.json','python -X utf8 scripts/phase2_query.py --dossier '+f['id'])]
    f['assets']=assets([r[0] for d in dev for r in core.execute('SELECT hash FROM finding_assets WHERE finding_id=?',(d['id'],))]);f['confidence_explanation']='人工整理，依獨立啟動／測試流程結構判為開發用途；不是自動廢案分數。';f['next_test']='按實際工具用途細分啟動、戰鬥、場景與動畫工作台，保留原始入口查證。';findings.append(f)
    # Preserve four other legacy IDs with rewritten, case-specific caveats.
    legacy={
      'NCA-59EB3E275366':('Ken Lee / MQ009：保留三次會面的孤立流程','hook、second_meeting、execution 場景仍在；目前只能確認入口未連通，不能沿用舊版的高信心判定。',['任務與對白','角色'],'現存英文字幕已翻譯，與 2021 年「未翻譯」敘述不一致；場景 payload 本身仍完整，沒有 MQ027 那種正式場景缺件證據。','按 mq009 檔名搜尋不到語音不代表語音不存在，下一步應追 voiceovermap ID。'),
      'NCA-8616011BE6ED':('無名 UI / Chevillon 介面依賴','未解析名稱的 widget 與 Chevillon 圖集形成一組可查的介面殘留；共享圖集本身仍有具名使用者。',['UI'],'10823073814826382310 的依賴通往 Chevillon centurion_ui 圖集與車內動畫；具名方向盤／車內 widget 同時引用相同圖集。','補齊 hash 字典及原生介面載入入口後，才能區分替代面板與孤立 widget。'),
      'NCA-E36DF3323A07':('Spiderbot / 原型名稱下的共用骨架','原型資料夾裡的機械零件與骨架仍被 Q005 動畫引用；資料夾名稱不足以定案。',['角色'],'Q005 的 sync_q005_06_spiderbot_room_01.anims 明確引用 prototype skeleton.rig；因此不能把這組 40 個相依資產整批當作廢案。','需要區分未使用外殼與仍被動畫使用的骨架，並追正式實體的 appearance 選擇。'),
      'NCA-AF6CA4611B50':('SQ017 / Chickentest 與主 quest 的關係','測試場景不是完全沒有來源：SQ017 的 quest 仍引用 chickentest 階段，是否能啟動要往上追入口。',['任務與對白'],'base\\quest\\side_quests\\sq017\\sq017.quest 引用 test\\sq017_chicken_test.questphase；只看 test 名稱會漏掉這條反證。','必須區分整個 SQ017 流程的正式入口與它內部測試分支，不從路徑推測實際執行。')}
    for i,(title,summary,cats,counter,next_test) in legacy.items():
        original=next(r for r in old if r['id']==i);detail=json.loads(original['details']);f=make(i,title,summary,cats)
        q=next((q for q in rules['quests'] if 'mq009' in q['prefix']),None) if 'MQ009' in title else None
        f.update(system_conclusion=(q['rule_status']+'；新規則分類 '+q['classification']) if q else '歷史候選保留；本階段沒有規則將它升為未使用。',analyst_conclusion='證據不足；保留為有具體反證的研究檔案。',community_note='歷史社群來源只作研究脈絡；第二階段未重新核實的說法不當成本版事實。',next_test=next_test)
        f['sections']=[section('目前可下的結論',summary,counter)];f['support']=[s for s in detail['support'] if s.startswith('可重查引用') or ('本機有 hook' in s) or ('無名 Widget' in s)];f['support']=f['support'] or ['第一階段已保存群內引用與來源校驗，可用下方查詢重現。']
        f['counter']=[counter,next_test];f['evidence']=[evidence('LEGACY-01','原始成員與引用','保留原 ID，重新區分歷史分類與目前判讀。',i,'python -X utf8 scripts/query.py --finding '+i)];f['confidence_explanation']='人工重新評估：存在上述具體使用／完整性反證，沒有足以確認未使用的排除證據；不採用第一階段手寫 score。';f['assets']=assets([r[0] for r in core.execute('SELECT hash FROM finding_assets WHERE finding_id=?',(i,))]);findings.append(f)
    # Two focused analyst studies; selection is disclosed, rules are untouched.
    studies=[('Items.SQ012_Shirt_VoteForPeralez','Peralez 競選上衣 / 發放指令不等於取得途徑','服裝'),('Items.sq018_jackie_machete','Jackie 的砍刀 / 任務物品與武器的界線','武器')]
    for name,title,cat in studies:
        r=next(r for r in rules['records'] if r['name']==name);ops=[x for x in operations if x['record']==name];f=make(ident('record-study:'+name),title,'',[cat])
        f.update(community='社群驗收指定；尚未核定不可取得',system_conclusion=r['rule_status']+'；規則分類 '+r['classification'],community_note='由使用者獨立清單選作人工案例；沒有加入發現規則或自動升級分類。',analyst_conclusion='證據不足；下面明確區分本機觀察與取得狀態。')
        if cat=='服裝':
            f['summary']='mws_jim 裡的上衣發放節點與圖入口斷開，但 SQ006 的同一件上衣實體仍被世界區塊引用。一條死路，並不能代表整個道具不可取得。'
            f['sections']=[section('一條斷開的發放路線',f"本機 Items.SQ012_Shirt_VoteForPeralez 共擷取 {len(ops)} 條任務操作見證。mws_jim 圖的節點 ID 151（handle 691）是 AddItem，數量 1，目標 refLocalPlayer=1。從該圖 input handle 1 沿所有輸出遍歷，沒有到達此節點。",'這是局部圖的結構斷開，不是條件機率，也沒有用 wiki 的分類替它加分。外部事件或原生派送尚未完全解析，因此仍保留靜態分析的界線。'),section('另一條不能忽略的世界引用','正式 EP1 gamedef 連到夜城 streamingworld，再到 blocks\\all.streamingblock、exterior_-2_-2_1_0.streamingsector，最後引用 base\\quest\\side_quests\\sq006\\entities\\sq006_peralez_shirt.ent。該實體的 itemTDBID 正是同一個上衣記錄。','因此可下的結論是：mws_jim 的那條發放路線斷開，但同一道具仍有世界實體引用。尚未驗證區塊啟動、可互動／可拾取狀態與存檔條件，不能裁定 wiki 必然錯誤，也不能確認玩家拿不到。')]
            f['support']=['節點 ID 151 的 AddItem 玩家發放指令存在，局部 input 圖遍歷為不可達。'];f['counter']=['SQ006 上衣實體的 itemTDBID 引用相同記錄，且可沿正式世界資源鏈到達。','世界實體是否啟動及允許拾取仍未實測；斷開的單一發放節點不足以排除世界取得途徑。'];f['next_test']='核對 exterior_-2_-2_1_0 區塊中上衣的啟動與互動設定，再觀察對應存檔的拾取狀態。'
        else:
            f['summary']='本機把 sq018_jackie_machete 定義成 Gen_Misc 任務物品，並非可裝備武器。不能把「不是武器」擴張成「整個物品未使用」。'
            f['sections']=[section('同一個名稱，兩種不同命題','Items.sq018_jackie_machete 的記錄型別是 gamedataItem_Record，itemType 為 Gen_Misc。這與一般 WeaponItem 記錄不同，支持「它不是一把可當普通武器使用的砍刀」這個較窄結論。','自動規則在所掃途徑中未觀察到取得鏈，將它列為定義線索。但它是否充當任務展示、檢查條件或動態生成物，仍未被排除；社群的不可取得說法不能因此自動成立。')]
            f['support']=['TweakDB 型別與 itemType 可直接重查，提供可裝備武器命題的結構反證。'];f['counter']=['Gen_Misc 仍可能是有效任務物品；缺少武器型別不是未使用證明。','沒有觀察到 shop／loot／reward 鏈，只界定本次靜態掃描結果，不能排除原生或動態記錄建立。'];f['next_test']='追 SQ018 的 inventory 檢查、任務物品生成與展示實體，分開驗證任務用途與玩家裝備用途。'
        f['evidence']=[evidence('REC-01','定義與所有已見途徑',r['rule_status'],name,r['reproduce']),evidence('REC-02','任務操作與逐層圖',f'{len(ops)} 條操作見證；無資料也照實顯示。','data/phase2/quest-operations.json','python -X utf8 scripts/phase2_query.py --operations '+name)]
        if cat=='服裝':f['evidence'].append(evidence('REC-03','另一條世界使用鏈','SQ006 實體指向相同上衣，不能因斷開發放節點而忽略。','3285049569572177738 /Data/RootChunk/compiledData/Data/Chunks/0/itemTDBID/$value','python -X utf8 scripts/phase2_query.py --route 3285049569572177738'))
        f['confidence_explanation']='人工案例選擇、規則輸出未修改。只有定義缺入口／可能使用鏈，缺執行與動態證據，因此維持證據不足。';f['sources']=['S-FANDOM','S-TWEAKS'];f['assets']=assets([x['hash'] for x in ops]+[a['target'] for a in r['asset_refs']]+([r['channels']['world_or_entity']['seed']['hash']] if cat=='服裝' and 'world_or_entity' in r['channels'] else []));findings.append(f)
    # All-category coverage includes negative results, not a manufactured quota.
    categories=['車輛','武器','服裝','角色','任務與對白','UI','開發者後台'];coverage=[]
    texts={
      '車輛':('未確認獨立廢棄載具','MQ027 新聞 AV 是共用 Zetatech Atlus 資源。Night Hunter 模組線索沒有可核對原版 ID，未列為發現。','駕駛／交通群、世界啟動條件、原生生成與模組所指 ID'),
      '武器':('一份用途辨析；沒有確認廢棄武器','Jackie 砍刀為 Gen_Misc 任務物品；Autoloader 存在定義殘留，取得途徑未獲證實。','動態物品生成、技能／版本語意與原生裝備判斷'),
      '服裝':('保留有爭議的發放與任務標籤證據','Peralez 上衣有 AddItem；其他清單服裝出現任務標籤清理或發放操作，不能只依分類頁宣判未使用。','節點條件、外層世界啟動、存檔與玩家取得實測'),
      '角色':('MQ027 三名角色構成有證據的內容群','Jessy、Stan、Kikil 的定義、實體、代理外觀與錄音可串連；不宣稱共用外觀完全未使用。','community phase 啟動、世界節點、動態外觀選擇'),
      '任務與對白':('MQ027 為旗艦；MQ009 維持證據不足','MQ027 的缺場景與斷開正式入口由通用規則找到。57 項 Archived Conversation 逐項比對，漏掉的保留為漏掉。','外部事件入口、原生流程、全部條件與執行追蹤'),
      'UI':('無名 widget 保留研究；未確認整組未使用','Chevillon 共用圖集仍有具名使用者。UI hash 名稱不完整，不能把無入向引用等同未使用。','原生 UI 載入、動態 widget 名稱與完整 hash 字典'),
      '開發者後台':('29 組合併為一份總覽','所有舊 ID 與 ENGRAM 連結保留。開發用途由人工整理明示，不計為 29 項新發現。','細分後台用途與每個入口的執行環境')}
    for cat in categories:
        rr=[r for r in rules['records'] if r['category']==cat];counts=dict(collections.Counter(r['rule_status'] for r in rr));h,result,gaps=texts[cat]
        labels={'HAS_USE_LINK':'有使用線索','ISOLATED_DEFINED_CONTENT':'孤立定義與資源','DEFINITION_ONLY':'僅定義','INDIRECT_REFERENCES_ONLY':'僅間接引用'}
        scope=(f"{len(rr):,} 個相關記錄；"+'、'.join(f'{labels[k]} {v:,}' for k,v in counts.items())+'。') if rr else ('83 個任務內容群與英文／繁中索引。' if cat=='任務與對白' else '第一階段已解碼 UI／任務資源與全資產引用。')
        coverage.append(dict(category=cat,headline=h,result=result,scope=scope+f"共 {rules['resource_scanned']:,} 份世界／實體資源變體；定義、世界、任務、腳本、商店、掉落、獎勵、製作與裝備鏈合併查核。",gaps=gaps+'；未知 flat 名稱、modded cache 是否生效與 archive 優先序亦未完全解決。',command='python -X utf8 scripts/phase2_rules.py\npython -X utf8 scripts/phase2_query.py'))
    manifest=read(ROOT/'reports/phase2/game-before.json');after=read(ROOT/'reports/phase2/game-after.json') if (ROOT/'reports/phase2/game-after.json').exists() else None
    integrity=f"遊戲 {config['game_product_version']} · GOG {config['gog_build']} · 5,151 檔案"+(' 前後校驗一致' if after and after['unchanged'] else '；結束校驗待執行')
    cases=[{k:v for k,v in r.items() if k in ('fixture_id','name','baseid','result','detail','attribution','origin','reproduce')} for r in holdout['cases']]
    catalogue=dict(schema='nca.public.research/v2',mode='private',game={k:config[k] for k in ('game_product_version','game_file_version','gog_version','gog_build')},source_manifest_sha256=manifest['sha256'],integrity=integrity,metrics=[{'value':'553,470','label':'已索引資產'},{'value':str(len(findings)),'label':'研究檔案／總覽'},{'value':'145','label':'MQ027 私人音訊'},{'value':str(len(cases)),'label':'獨立驗收項目'}],findings=findings,aliases=aliases,coverage=coverage,acceptance={'headline':'逐項結果：'+ ' · '.join(f'{k} {v}' for k,v in holdout['counts'].items()),'notes':['A 類與 57 項對話清單：只有找到殘留、未達預期不可取得分類者，照實記為「漏掉／待核」。C 類正面使用對照與 B 類殘留調查另按各自預期回報。','對不可取得命題，所有正面案例仍未完成執行驗證。漏掉如實列出；沒有證據就不宣稱 wiki 有誤或版本差異。','規則輸出先產生並固定 SHA-256，再讀使用者清單。驗收器不修改發現、分類或信心。','TCRF 本階段未讀。分類快照的 57 個標題有來源及 CC-BY-SA 註記；沒有公開完整對話。'], 'cases':cases},method=[{'title':'分類的來源','paragraphs':['每份檔案分列規則、研究判讀與社群說法。MQ027 的疑似刪除來自通用條件；案例選擇與敘事則明標人工。','第一階段的手寫 score 不再作為信心依據。檢查途徑數只是覆蓋度，不能換算為廢案機率。']},{'title':'可重算的信心','paragraphs':['無正式流程入口且有缺失場景 payload，才標示疑似刪除。只有名稱、孤立定義或零入向引用，一律證據不足。','未排除原生、動態與存檔入口，沒有任何內容升級為確認遊戲內未使用。'],'command':'python -X utf8 scripts/phase2_rules.py'},{'title':'覆蓋與保守推論','paragraphs':rules['limits']+['所有已安裝 streamingsector 都視為可能入口，避免尚未解算啟動遮罩時誤報未使用。','graph 操作分析沿所有條件輸出遍歷；外部事件與原生派送沒有被模擬。']},{'title':'版本與重建','paragraphs':[integrity,'原始遊戲只讀；核心與補充證據資料庫均由保存的索引／解碼輸入重建。完整遊戲媒體、文字與機器轉錄只留私人版。'],'command':'python -X utf8 scripts/phase2_verify.py'}],sources=sources)
    historical_community={f['id'] for f in old if f['community']=='社群已記錄'}
    for f in findings:f['community_status']='has_lead' if f['id'] in historical_community or any(s in f['sources'] for s in ('S-FANDOM','S-MQ027-HISTORY')) else 'unmatched'
    write(ROOT/'web/catalogue.json',catalogue);private={'audio':mq['audio'],'localization':mq['localization']}
    for a in private['audio']:
        file=a['path'].split('\\')[-1];a['role']='Jessy' if file.startswith('civ_mid_f') else 'Suicide Stan' if file.startswith('civ_low_m') else 'Kikil' if file.startswith('civ_mid_m') else 'V' if file.startswith('v_') else '角色待核定'
        a['gender']='語音版本 '+('/'.join(sorted({m['variant'].replace('ResPath','') for m in a['voice_map']})))
        src=OUT/'audio'/a['file'];dst=ROOT/'data/media'/a['file']
        if not dst.exists():shutil.copyfile(src,dst)
    private['role_mapping_note']='依 voice actor prefix 與角色文本交叉判讀；未人工逐段校對。';write(ROOT/'web/mq027-private.json',private)
    public=dict(catalogue,mode='public');write(PUBLIC/'docs/catalogue.json',public)
    preview=ROOT/'web/public-preview';preview.mkdir(exist_ok=True)
    if not (ROOT/'web/legacy.html').exists():shutil.copyfile(ROOT/'web/index.html',ROOT/'web/legacy.html')
    for folder in (ROOT/'web',PUBLIC/'docs',preview):
        shutil.copyfile(ROOT/'web/phase2.html',folder/'index.html')
        if folder!=ROOT/'web':
            for name in ('phase2.css','phase2.js'):shutil.copyfile(ROOT/'web'/name,folder/name)
    write(preview/'catalogue.json',public);write(ROOT/'exports/phase2-aliases.json',aliases)
    # v1 consumers retain fields; additions are optional provenance/redirects.
    previous=ROOT/'exports/engram-findings-phase1.jsonl'
    if not previous.exists():shutil.copyfile(ROOT/'exports/engram-findings.jsonl',previous)
    prior=[json.loads(x) for x in previous.read_text(encoding='utf-8').splitlines()];byid={r['id']:r for r in prior};classification={'確認遊戲內未使用':'confirmed_unused','疑似刪除內容':'suspected_cut','測試或開發殘留':'test_or_dev_remnant','證據不足':'insufficient_evidence'}
    for f in findings:
        r=dict(byid.get(f['id'],prior[0]));r.update(id=f['id'],title=f['title'],category=' / '.join(f['categories']),classification=classification[f['classification']],classification_origin=f['classification_origin'],community_status=f['community'],interpretation=f['summary'],support=f['support'],counterevidence=f['counter'],structural_evidence=f['evidence'],sources=[s for s in sources if s['id'] in f['sources']],reproduce={'command':'python -X utf8 scripts/phase2_query.py --dossier '+f['id'],'sql':''},assets=[{'asset_id':'NCA-ASSET-'+a['hash'],'path':a['path'],'extension':a['extension'],'role':'related','variants':[{'archive':v['path'],'archive_sha256':v['sha256'],'entry_sha1':v.get('entry_sha1')} for v in a['archives']]} for a in f['assets']],source_manifest_sha256=manifest['sha256'],scan_id='NCA-SCAN-'+manifest['sha256'][:16].upper());byid[f['id']]=r
    for oldid,newid in aliases.items():byid[oldid].update(superseded_by=newid,record_status='merged_alias',classification_origin='phase1_historical_analyst')
    (ROOT/'exports/engram-findings-phase2.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in byid.values()),encoding='utf-8')
    shutil.copyfile(ROOT/'exports/engram-findings-phase2.jsonl',ROOT/'exports/engram-findings.jsonl')
    for filename,heading in [('MQ027.md','MQ027 旗艦研究檔案'),('FINDINGS.md','第二階段研究檔案')]:
        rows=[f'# {heading}','',integrity,'']
        for f in findings[:1] if filename=='MQ027.md' else findings:
            rows += ['## '+f['title'],'',f"`{f['id']}` · {f['classification']} · {f['classification_origin']}",'',f['summary'],'','系統：'+f['system_conclusion'],'','研究判讀：'+f['analyst_conclusion'],'']
            for s in f['sections']:rows+=['### '+s['heading'],'']+sum(([p,''] for p in s['paragraphs']),[])
            rows+=['### 反證','']+['- '+x for x in f['counter']]+['','### 證據與重跑','']
            for ev in f['evidence']:rows += [f"**{ev['id']} {ev['label']}** — {ev['observation']}",'','```text',ev['locator'],ev['command'],'```','']
            rows += [f['confidence_explanation'],'']
        (ROOT/'research/phase2'/filename).write_text('\n'.join(rows),encoding='utf-8')
    print(json.dumps({'findings':len(findings),'aliases':len(aliases),'cases':len(cases),'engram_records':len(byid)},ensure_ascii=False))

if __name__=='__main__':main()
