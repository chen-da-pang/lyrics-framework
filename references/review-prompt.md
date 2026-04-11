# Review Prompt Template

Use this exact structure when asking Qwen to review three lyric versions.

---

```
请将以下三个版本的歌词整理成一个 Markdown 文件，保存到 {output_path}。

格式要求：
- 每个版本都要有标题（版本名 + 主韵）
- 每句歌词完整列出，格式：L01 歌词内容
- 每个版本后面紧跟审核结果，审核内容包括：
  1. 逐句检查字数是否符合框架要求（标出不符合的句子）
  2. 逐句检查押韵是否正确（[押主韵]的句子是否真的押了，[掺韵]的句子是否真的没押）
  3. Hook句是否在所有位置完全一致
  4. S5/S6是否是S1/S2的压缩回返（不是完全复制，也不是重新创作）
  5. 总体评价（主题感觉、意象质量）
- 审核要逐句写，不能用「L22-L39全部正确」这种省略写法
- 末尾输出三版横向对比表格，推荐最佳版本并说明理由

框架字数要求（用于审核）：
{char_requirements}

押韵框架要求：
{rhyme_requirements}

---

版本一：{model_1_name}（主韵：{model_1_rhyme}）
{model_1_lyrics}

---

版本二：{model_2_name}（主韵：{model_2_rhyme}）
{model_2_lyrics}

---

版本三：{model_3_name}（主韵：{model_3_rhyme}）
{model_3_lyrics}
```

---

## How to fill the template

**{char_requirements}**: List each line's required char count, e.g.:
```
L01=3字, L02=11字, L03=10字, L04=8字
L05=14字, L06=10字, L07=5字
...
```
Read from `framework-fillable.md`.

**{rhyme_requirements}**: List which lines need main rhyme vs. 掺韵 vs. 散韵, e.g.:
```
L07,L08,L09,L11,L12... = 押主韵
L10,L14,L24,L28 = 掺韵（不押主韵）
其余 = 散韵（自由）
```
Read from `framework-fillable.md`.

**{output_path}**: `{framework_dir}/lyrics-comparison.md`
