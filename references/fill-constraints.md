# Fill Prompt Hard Constraints

Include these verbatim in every fill prompt for Sub-workflow B:

```
- 不能使用 [原曲主韵] 作为主韵，自选其他韵
- 严格遵守每句字数，不能多也不能少
- Hook句在全曲所有标注「← Hook句」的位置完全重复，一字不差
- [押主韵]的句子句尾必须押选定的主韵
- [掺韵]的句子故意不押主韵
- S5/S6必须是S1/S2的压缩回返，不能重新创作新内容
- 只输出歌词，每句标注行号，不要输出其他内容
```

Replace `[原曲主韵]` with the actual main rhyme vowel extracted from `framework.yaml` → `rhyme_style`.
