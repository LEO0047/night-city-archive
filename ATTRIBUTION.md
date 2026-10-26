# Attribution and provenance

This repository distributes project source code and research metadata. It does not bundle Cyberpunk 2077 game archives, extracted resources, subtitle corpora, models, textures, audio, or the private SQLite database.

| Upstream | Use | License / source |
|---|---|---|
| WolvenKit 9.1.0 | ArchiveReader, HashService, CR2WReader, RedJsonSerializer and local GLB/PNG export | [Official release](https://github.com/WolvenKit/WolvenKit/releases/tag/9.1.0), GPL-3.0; full notice in `research/WolvenKit-LICENSE.txt`. Binaries are downloaded by the user from upstream, not repackaged here. |
| REDmodding Wiki | CLI and format documentation | [CLI command list](https://wiki.redmodding.org/wolvenkit/wolvenkit-cli/usage/command-list). Linked and summarized, not mirrored. |
| spuddeh/cp2077-ink-archive | `scripts/ink_paths.py` adapts its DepotPath traversal. Database and UI research informed the project. Two unresolved resources are independent regression targets. | [Repository](https://github.com/spuddeh/cp2077-ink-archive), MIT; full notice in `research/ink-archive-LICENSE.txt`. Upstream 2.31 game data is not redistributed or represented as this project's 2.5 scan. |
| WolvenKit Cyberpunk Blender add-on | Investigated as the extension path for complete materials, entities and animations; not installed or copied | [Official repository](https://github.com/WolvenKit/Cyberpunk-Blender-add-on). |
| Three.js r180 | Local WebGL model viewer, OrbitControls, GLTFLoader and BufferGeometryUtils | [Source](https://github.com/mrdoob/three.js/tree/r180), MIT, `web/vendor/three-LICENSE.txt`. GLTFLoader's utility import was changed to a local relative path. |
| vgmstream r2168 | Local Wwise WEM decoding | [Official release](https://github.com/vgmstream/vgmstream/releases/tag/r2168). Downloaded by the user; upstream COPYING notices remain with its package. |
| libSpace, 2021 | Historical MQ009 / untranslated-content research | [First-person research post](https://www.reddit.com/r/LowSodiumCyberpunk/comments/lsc5p1/). Summarized with uncertainty and explicit version differences. |
| cqb02rmse8ri, 2021 | Quest grouping and cautions about numbering, renaming and rewriting | [First-person research post](https://www.reddit.com/r/cyberpunkgame/comments/lmk5hr/). Numbering gaps are not treated as proof of removal. |
| The Cutting Room Floor | Attempted research source; HTTP 403 during collection | [Cyberpunk 2077](https://tcrf.net/Cyberpunk_2077). Unread content is not treated as verified evidence. |

`research/upstream-pins.json` records commits observed during research. `scripts/tools.lock.json` pins the official binary download URLs, byte lengths and SHA-256 values. `research/tool-files.json` records the files used for the reference scan; a locally compiled bridge can have a different binary hash.

The complete thin adapter is provided in `scripts/WolvenBridge.cs`; archive format and compression implementations remain upstream WolvenKit code. New project code is GPL-3.0, while independently licensed MIT dependencies retain their notices. The licenses do not apply to the original game's proprietary content.

## 第二階段新增來源

- [redscript / jac3km4](https://github.com/jac3km4/redscript)，MIT。使用固定 v0.5.32 CLI 對本機 final.redscripts 反編譯，未修改遊戲；此倉庫不包含反編譯後的遊戲程式。
- WolvenKit 的 DynamicChunk／ReadCHandle 與 TypeGlobal 相容性處理，沿用上游 GPL-3.0-or-later；來源定位見 [第二階段來源表](research/phase2/sources.json)。
- Cyberpunk Wiki contributors 的分類標題清單，依 CC-BY-SA 標示來源與衍生整理，詳見 [HOLDOUT-ATTRIBUTION](research/phase2/HOLDOUT-ATTRIBUTION.md)。沒有轉載遊戲完整對話。
- 外部資料不可讀的情況逐項記錄。TCRF 本階段未讀，未繞過限制。
