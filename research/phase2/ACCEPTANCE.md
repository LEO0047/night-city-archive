# 第二階段驗收報告

遊戲 2.5 · GOG 60152385347545148 · 5,151 檔案 前後校驗一致

## 結論與界線

技術驗證 23 / 23；這不代表社群廢案清單已全部通過。

MQ027 的「未接正式流程＋六個正式場景缺件」支持疑似刪除。Peralez 上衣同時具有斷開的發放節點及世界實體引用，維持證據不足。Jackie 砍刀是 Gen_Misc 任務物品，不能把非武器當成整件未使用。

社群 A 類 18 項及 Archived Conversation 57 項共 75 個驗收列，皆未達不可取得分類，嚴格計為漏掉／待核。這些列可能包含相同內容的例子，不是 75 個已確認不同廢案。七項正式實裝反例均未誤判；兩項改版移除線索另只回報殘留。

沒有證據就不把漏掉歸咎於 wiki 錯誤或版本差異。原始清單保持獨立，未加入發現規則。一般節點分析在收到清單後開發，因此不宣稱預註冊盲測。

## 技術驗收逐條

| 檢查 | 結果 |
|---|---|
| rule_source_matches_output | 通過 |
| holdout_freezes_rule_output | 通過 |
| discovery_does_not_import_holdout_or_fixture_ids | 通過 |
| all_record_classifications_recomputed | 通過 |
| quest_confidence_from_two_observations | 通過 |
| seven_active_controls_not_cut | 通過 |
| holdout_reports_every_explicit_and_archived_case | 通過 |
| mq027_independent_rule_and_six_formal_missing_scenes | 通過 |
| no_confirmed_unused_without_runtime_exclusion | 通過 |
| unique_case_summaries_and_counterevidence | 通過 |
| classification_provenance_and_reproduction_visible | 通過 |
| all_34_old_ids_preserved_29_aliases | 通過 |
| engram_v1_fields_and_redirects_preserved | 通過 |
| 145_audio_payloads_checksums_maps_and_asr_labels | 通過 |
| public_catalogue_excludes_private_long_text | 通過 |
| public_schema_and_payload_boundary | 通過 |
| world_decode_gaps_are_explicit | 通過 |
| 5151_original_game_files_unchanged | 通過 |
| phase1_acceptance_still_passes | 通過 |
| phase1_fresh_rebuild_matches | 通過 |
| phase2_fresh_rebuild_matches_all_tables | 通過 |
| rule_rerun_identical | 通過 |
| within_approved_capacity | 通過 |

補充資料庫重新建立後，14 張表的列數與內容指紋一致。原始資料庫約 5 GB，先建立並驗證 638,826,765 bytes 壓縮復原副本，成功後移除；重建未同時保留兩份完整資料庫。

世界／實體選取 86,585 份 archive 變體，成功 86,579，未解析 6。三個不同資產分別出現於本體及 EP1 封存檔；錯誤為 AccessPoint／Window／WindowBlinders skill-check 型別不匹配，未強制補造內容。

原始遊戲前後 SHA-256 manifest：`3f137afbc4c672b2b0596be2dc29d5030b23c8d87076190741f3ad3e374f6b86`。新增、刪除、變更皆為 0；共 5,151 檔案。

第一階段的 25 項驗收另行重跑通過。原本「至少 30 組」檢查仍對歷史核心快照運行；第二階段展示將 29 組合併為 1 份，沒有拿歷史數量替新成果充數。

## 逐項獨立清單

| ID | 項目 | 回報 | 具體觀察與原因 |
|---|---|---|---|
| USER-A-01 | Fake SEMURAI jacket | 漏掉 | 已對應 Items.mq017_SameraiJacket；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot, quest_or_scene, world_or_entity；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-02 | BAD MOTHERFUCKER vest | 漏掉 | 已對應 Items.SQ021_Wraiths_Vest；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：quest_or_scene, world_or_entity；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-03 | Kang Tao lab suit | 漏掉 | 已對應 Items.SQ021_Lab_Costume；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：quest_or_scene, world_or_entity；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-04 | Peralez campaign shirt | 漏掉 | 已對應 Items.SQ012_Shirt_VoteForPeralez；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：quest_or_scene, world_or_entity；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-05 | Predator exo-jacks (from Rogue) | 漏掉 | 已對應 Items.Q115_Custom_Predator_Boots；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-06 | Autoloader | 漏掉 | 已對應 Items.SimpleWeaponMod16；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-07 | Jackie's Machete | 漏掉 | 已對應 Items.sq018_jackie_machete；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。本機型別為 gamedataItem_Record / Gen_Misc，不能把「非可用武器」改寫成「整個任務物品未使用」。 |
| USER-A-08 | BD: Foreign Body | 漏掉 | 已對應 Items.q105_braindance_foreign_body；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-09 | BD: sASSquatch | 漏掉 | 已對應 Items.q105_braindance_sassquatch；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-10 | Sora-II | 漏掉 | 已對應 Items.generic_q115_afterlife_weapon_dealer；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-11 | Vehicle Inventory | 漏掉 | 已對應 Items.generic_q112_warehouse_roster；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-12 | NetWatch: Operation Eternal | 漏掉 | 已對應 Items.q110_equipment_requisition_list；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-13 | CLASSIFIED/To do/Priority P0 | 漏掉 | 已對應 Items.q306_blackops_orders；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-14 | Dossier on Chester Bennett | 漏掉 | 已對應 Items.mq304_bennett_dossier_shard；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-15 | ARTHUR CORMAC CORMAC | 漏掉 | 已對應 Items.ep1_generic_cormac_shard；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-16 | Get him talking | 漏掉 | 已對應 Items.sts_cct_cpz_01_shard_003；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot, quest_or_scene；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-17 | Archived Conversation example: Kabuki | 漏掉 | 已對應 Items.sts_wat_kab_101_onscreen_001；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-A-18 | Archived Conversation example: Badlands | 漏掉 | 已對應 Items.ma_bls_ina_se5_14_onscreen_01；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot, quest_or_scene；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-B-01 | Tabula e-Rasa | 找到 | 目前對應 1 個記錄，1 個本機名稱鍵。已對應 Items.PerkPointsResetter；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| USER-B-02 | Trajectory Generator | 未找到殘留 | 目前對應 0 個記錄，0 個本機名稱鍵。已查目前兩份 canonical TweakDB、英文螢幕文字與日誌，未完成對應。不能因為這次沒找到就宣稱已從遊戲刪除。 |
| USER-C-01 | Gig: Nasty Hangover | 找到 | 正式流程連通的場景／階段：7；系統疑似刪除標記：0。 |
| USER-C-02 | Gig: Concrete Cage Trap | 找到 | 正式流程連通的場景／階段：16；系統疑似刪除標記：0。 |
| USER-C-03 | Gig: Desperate Measures | 找到 | 正式流程連通的場景／階段：11；系統疑似刪除標記：0。 |
| USER-C-04 | NCART metro | 找到 | 正式流程連通的場景／階段：1；系統疑似刪除標記：0。NCART 另有 2.1 官方實裝記錄；此項要求本機引用也能對上，沒有以官方資料替系統補分。 |
| USER-C-05 | Q000 Nomad | 找到 | 正式流程連通的場景／階段：69；系統疑似刪除標記：0。 |
| USER-C-06 | MQ008 shooting contest | 找到 | 正式流程連通的場景／階段：9；系統疑似刪除標記：0。 |
| USER-C-07 | EP1 MQ301 | 找到 | 正式流程連通的場景／階段：16；系統疑似刪除標記：0。 |
| WIKI-AC-01 | Archived Conversation: Ayo Zarin and Slider | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-02 | Archived Conversation: Bartolomeo and Jack | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-03 | Archived Conversation: Bex and Annie | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-04 | Archived Conversation: Brendan Rock and Andreas Chinnook | 漏掉 | 已對應 Items.q306_blackops_camo；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-05 | Archived Conversation: Carl "Dodger" Robinson and Chester Bennett | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-06 | Archived Conversation: Casper Tyc and Eddie Friedman | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-07 | Archived Conversation: Commissioner Fawlter and Dr. Shipman | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-08 | Archived Conversation: Dan and Dr Carl | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-09 | Archived Conversation: Darwin Blum and Necole Esperon | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-10 | Archived Conversation: Dave Crystal and Victor Byrnes | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-11 | Archived Conversation: Dewey and Jen | 漏掉 | 已對應 Items.generic_gas_station_06；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-12 | Archived Conversation: Doug and Kim | 漏掉 | 已對應 Items.generic_q112_warehouse_ammo；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-13 | Archived Conversation: Drew Furey and Lesli Furey | 漏掉 | 已對應 Items.ma_bls_ina_se5_14_onscreen_01；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot, quest_or_scene；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-14 | Archived Conversation: Eisaku and Salman | 漏掉 | 已對應 Items.generic_q113_estate_cash_bribe；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-15 | Archived Conversation: Ellis and Gottfrid | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-16 | Archived Conversation: Evan Groger and Lucy Miller | 漏掉 | 已對應 Items.ma_cct_cpz_101_onscreen_01；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-17 | Archived Conversation: Gaston Philips and Padre | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-18 | Archived Conversation: Genzo and Hiroto | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-19 | Archived Conversation: Gianni and 8ug8ear | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-20 | Archived Conversation: Gianni and Hal | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-21 | Archived Conversation: Gilfoyle and Rad Rob | 漏掉 | 已對應 Items.generic_q113_arasaka_lobby；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-22 | Archived Conversation: Gustaf Ekland and Arif Ekmek | 漏掉 | 找到 2 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-23 | Archived Conversation: Hex and Naima | 漏掉 | 已對應 Items.generic_q114_nomads_buster；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-24 | Archived Conversation: Hideharu and Fuyuki | 漏掉 | 已對應 Items.generic_q113_arasaka_stash；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-25 | Archived Conversation: Hideo Ito and Satoko Ito | 漏掉 | 已對應 Items.ma_wbr_hil_02_onscreen_03；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-26 | Archived Conversation: Holler and Bex | 漏掉 | 已對應 Items.generic_q110_mall_boss_sentry；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-27 | Archived Conversation: Iori and R00tifer | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-28 | Archived Conversation: Izaiah and Meena | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-29 | Archived Conversation: Jock and Tommy | 漏掉 | 已對應 Items.generic_q110_mall_sentry；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-30 | Archived Conversation: Joel and Lennie | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-31 | Archived Conversation: Jotaro and Karubo | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-32 | Archived Conversation: Julia Bonet and Ivan Vassiliev | 漏掉 | 已對應 Items.ma_std_rcr_01_onscreen_02；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot, quest_or_scene；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-33 | Archived Conversation: Kanna and Aimoto | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-34 | Archived Conversation: Kelly Miller and Tanner Sheridan | 漏掉 | 已對應 Items.ma_wat_nid_34_onscreen_01；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-35 | Archived Conversation: Kenji Sakura and Mario Casey | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-36 | Archived Conversation: Kevin and Max | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-37 | Archived Conversation: Kevin Edvards and Padre | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-38 | Archived Conversation: Kieran Koecher and Ovide Labat | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-39 | Archived Conversation: Kim and Joey | 漏掉 | 已對應 Items.generic_q112_warehouse_guard；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-40 | Archived Conversation: Kim and Wendy | 漏掉 | 已對應 Items.generic_q112_warehouse_contractor；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-41 | Archived Conversation: Lars and Gina | 漏掉 | 已對應 Items.generic_q113_estate_gift；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-42 | Archived Conversation: Lene and Viper | 漏掉 | 已對應 Items.generic_q110_mall_steroids；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-43 | Archived Conversation: Mano Viel and Gottfrid | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-44 | Archived Conversation: Maxim Reese and Adam Newell | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-45 | Archived Conversation: Necole Esperon and Duncan Lanterman | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-46 | Archived Conversation: Ollie and Karubo | 漏掉 | 已查目前兩份 canonical TweakDB、英文螢幕文字與日誌，未完成對應。不能因為這次沒找到就宣稱已從遊戲刪除。 |
| WIKI-AC-47 | Archived Conversation: Ollie and Yvon | 漏掉 | 已對應 Items.generic_q113_estate_burglar；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-48 | Archived Conversation: Oscar Jones and Zoe "Víbora" Roja | 漏掉 | 已對應 Items.ma_std_arr_101_onscreen_01；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-49 | Archived Conversation: Rob and Mia | 漏掉 | 已對應 Items.generic_sq004_score；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-50 | Archived Conversation: Rufus and Angie | 漏掉 | 已對應 Items.generic_q115_afterlife_flirt；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-51 | Archived Conversation: Russel Greene and Jae-Hyun | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-52 | Archived Conversation: Salman and Chesterfield | 漏掉 | 已對應 Items.generic_q113_estate_containers；規則結果 DEFINITION_ONLY。自動列出缺少已觀察使用入口的定義線索。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-53 | Archived Conversation: Salman and Uhlmann | 漏掉 | 已對應 Items.generic_q113_estate_lost_valuables；規則結果 HAS_USE_LINK。系統保留使用關係，沒有把它列作孤立內容。已見途徑：loot；這是可能使用鏈，並非實際取得紀錄。不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。 |
| WIKI-AC-54 | Archived Conversation: Sam Milton and Russel Greene | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-55 | Archived Conversation: Trauma Team Dispatch and Arthur Jacobs | 漏掉 | 已查目前兩份 canonical TweakDB、英文螢幕文字與日誌，未完成對應。不能因為這次沒找到就宣稱已從遊戲刪除。 |
| WIKI-AC-56 | Archived Conversation: Yalitiza Sigman and Ramon Guizar | 漏掉 | 找到 1 個文字鍵與 1 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |
| WIKI-AC-57 | Archived Conversation: Yuki Amano and Darwin Blum | 漏掉 | 找到 1 個文字鍵與 0 條日誌路徑，但尚未對應到可驗證的道具使用鏈。 |

## 外部來源與讀取限制

Cyberpunk Wiki 分類以快照取得 57 個對話標題；直接頁面存取有 403／402 或快取未命中，未繞過。TCRF 本階段未讀。1.6 與 2.1 實裝反例另有 CD PROJEKT RED 官方更新記錄。來源 URL、授權與限制見 [sources.json](sources.json) 及 [HOLDOUT-ATTRIBUTION.md](HOLDOUT-ATTRIBUTION.md)。

## 網站與公開差異

私人版：MQ027 全文研究、145 個原音、原始日誌與未校對離線轉錄；可連回模型、圖片、UI 結構及全域全文索引。公開版：研究敘述、定位路徑、識別碼與校驗；沒有媒體、完整對白或資料庫。

瀏覽器已驗證載入、類別篩選、反例搜尋、舊 ID 轉址、私人語音播放至結束與既有模型載入；公開版未顯示音訊或私人讀取入口。截圖 API 回報無法擷取，因此本次沒有以截圖宣稱像素／響應式視覺驗收。

截至本報告，GitHub 與公開網站尚未更新。推送前需使用者檢視具體差異並批准。
